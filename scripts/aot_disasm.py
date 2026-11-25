#!/usr/bin/env python3
"""Read-only helper: disassemble Dart AOT functions that Blutter lists without a body.

Blutter (Dart 3.12, dwarf_stack_traces_mode) knows every function's entry point
(ida_script/addNames.py) but reports `size: -0x1` for most of them because the
Code objects were discarded. This tool:
  * takes all entry points from addNames.py, sorts them and uses the next entry
    point as the end of each function (upper bound, may include padding);
  * disassembles that range of libapp.so with Capstone (ARM64);
  * annotates object-pool loads (Dart ARM64 PP register = x27) using pp.txt.

It never writes to the APK or libapp.so. Output goes to stdout.

Usage:
  python aot_disasm.py <libapp.so> <blutter_out_dir> fn <addr|name-substring> [...]
  python aot_disasm.py <libapp.so> <blutter_out_dir> xref <pp_offset> [...]
      list functions whose code loads the given pool offsets (e.g. 0xe448)
Requires: capstone (pip install capstone).
"""
import bisect
import re
import sys
from pathlib import Path

import capstone

NAME_RE = re.compile(r'idaapi\.set_name\((0x[0-9a-f]+), "([^"]+)"\)')
PP_RE = re.compile(r'^\[pp\+(0x[0-9a-f]+)\] (.*)$')


def load_functions(out_dir: Path):
    fns = {}
    for m in NAME_RE.finditer((out_dir / "ida_script" / "addNames.py").read_text(encoding="utf-8")):
        addr, name = int(m.group(1), 16), m.group(2)
        if name.endswith("_check"):
            continue
        fns.setdefault(addr, name)
    addrs = sorted(fns)
    return addrs, fns


def load_pool(out_dir: Path):
    pool = {}
    for line in (out_dir / "pp.txt").read_text(encoding="utf-8").splitlines():
        m = PP_RE.match(line)
        if m:
            pool[int(m.group(1), 16)] = m.group(2)[:120]
    return pool


class Disasm:
    def __init__(self, lib: Path, out_dir: Path):
        self.data = lib.read_bytes()
        self.addrs, self.names = load_functions(out_dir)
        self.pool = load_pool(out_dir)
        self.cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        self._add_call_targets()

    def _add_call_targets(self):
        """Every `bl` target inside the code range is also a function start."""
        lo, hi = self.addrs[0], self.addrs[-1] + 0x400
        code = self.data
        for pos in range(lo, min(hi, len(code)) - 3, 4):
            w = int.from_bytes(code[pos:pos + 4], "little")
            if (w >> 26) == 0b100101:  # BL imm26
                imm = w & 0x3FFFFFF
                if imm & 0x2000000:
                    imm -= 1 << 26
                tgt = pos + imm * 4
                if lo <= tgt < hi and tgt not in self.names:
                    self.names[tgt] = f"sub_{tgt:x}"
        self.addrs = sorted(self.names)

    def bounds(self, addr):
        i = bisect.bisect_right(self.addrs, addr) - 1
        start = self.addrs[i]
        end = self.addrs[i + 1] if i + 1 < len(self.addrs) else start + 0x400
        return start, end

    def insns(self, start, end):
        """Yield (insn, pool_offset_or_None). Tracks `add xN, x27, #hi, lsl #12` pairs."""
        hi = {}
        for ins in self.cs.disasm(self.data[start:end], start):
            off = None
            ops = ins.op_str.replace(" ", "")
            m = re.match(r'(x\d+),x27,#(0x[0-9a-f]+|\d+),lsl#12$', ops)
            if ins.mnemonic == "add" and m:
                hi[m.group(1)] = int(m.group(2), 0) << 12
            m = re.search(r'\[(x\d+),#(0x[0-9a-f]+|\d+)\]', ops)
            if ins.mnemonic in ("ldr", "ldp") and m:
                base, imm = m.group(1), int(m.group(2), 0)
                if base == "x27":
                    off = imm
                elif base in hi:
                    off = hi.pop(base) + imm
            yield ins, off

    def dump(self, addr):
        start, end = self.bounds(addr)
        print(f"\n// {self.names[start]}  [{start:#x}, {end:#x})")
        for ins, off in self.insns(start, end):
            note = f"  ; [pp+{off:#x}] {self.pool.get(off, '?')}" if off is not None else ""
            if ins.mnemonic == "bl":
                tgt = int(ins.op_str.lstrip("#"), 16)
                note = f"  ; -> {self.names.get(tgt, '?')}"
            print(f"  {ins.address:#08x}: {ins.mnemonic:8} {ins.op_str}{note}")

    def xref(self, offsets):
        want = set(offsets)
        hits = {}
        for i, start in enumerate(self.addrs):
            end = self.addrs[i + 1] if i + 1 < len(self.addrs) else start + 0x400
            for ins, off in self.insns(start, end):
                if off in want:
                    hits.setdefault(start, set()).add(off)
        for start, offs in sorted(hits.items()):
            print(f"{start:#x} {self.names[start]}: " + ", ".join(f"{o:#x}" for o in sorted(offs)))


def main(argv):
    lib, out_dir, cmd, *args = argv
    d = Disasm(Path(lib), Path(out_dir))
    if cmd == "fn":
        for a in args:
            if a.startswith("0x"):
                d.dump(int(a, 16))
            else:
                for addr in d.addrs:
                    if a in d.names[addr]:
                        d.dump(addr)
    elif cmd == "xref":
        d.xref([int(a, 16) for a in args])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
