#!/usr/bin/env python3
"""Read-only: print Dart AOT snapshot fingerprint for both ABIs of an APK.

Usage: python -I scripts/fingerprint_snapshot.py local/input/base_1.apk
Prints libapp/libflutter SHA-256, snapshot version hash, snapshot feature flags
and the Dart version string. No execution, no network, writes nothing.
"""
import hashlib
import re
import sys
import zipfile

MAGIC = b"\xf5\xf5\xdc\xdc"  # Dart snapshot magic


def main(apk: str) -> int:
    z = zipfile.ZipFile(apk)
    for abi in ("arm64-v8a", "armeabi-v7a"):
        try:
            app = z.read(f"lib/{abi}/libapp.so")
            fl = z.read(f"lib/{abi}/libflutter.so")
        except KeyError:
            print(f"== {abi}: not present")
            continue
        print(f"== {abi}")
        print("  libapp.so     ", len(app), hashlib.sha256(app).hexdigest())
        print("  libflutter.so ", len(fl), hashlib.sha256(fl).hexdigest())
        for m in re.finditer(re.escape(MAGIC), app):
            o = m.start()
            # layout: magic(4) length(8) kind(8) version_hash(32) features(cstr)
            ver = app[o + 20:o + 52].decode("latin1")
            feat = app[o + 52:o + 300].split(b"\0")[0].decode("latin1")
            print(f"  snapshot @{o:#x} hash={ver}")
            print(f"    features: {feat}")
        for s in sorted(set(re.findall(rb"\d+\.\d+\.\d+ \(stable\)[^\0]{0,60}", fl))):
            print("  dart:", s.decode("latin1"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
