#!/usr/bin/env python3
"""Read-only validation of handoff files. No execution of APK, no network."""
import hashlib, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def main():
    manifest=ROOT/'local/SHA256SUMS.json'
    if not manifest.is_file():
        print('BLOCKED: local artifacts absent; transfer private handoff separately.'); return 2
    bad=[]
    for e in json.loads(manifest.read_text(encoding='utf-8')):
        p=ROOT/e['path']
        if not p.is_file() or p.stat().st_size!=e['bytes'] or sha(p)!=e['sha256']:
            bad.append(e['path']); print('FAIL',e['path'])
    if bad: return 1
    with zipfile.ZipFile(ROOT/'local/input/base_1.apk') as a, zipfile.ZipFile(ROOT/'local/build/PowerBox_2.1.1_Blockly_TEST.apk') as b:
        assert a.testzip() is None and b.testzip() is None
        assert set(a.namelist())==set(b.namelist())
        changes={n for n in a.namelist() if a.read(n)!=b.read(n)}
        expected={'assets/flutter_assets/assets/html/'+n for n in ('index.html','index_3.html','index_32.html','index_4.html','index_6.html','index_l.html')}
        assert changes==expected, changes
        print('PASS: CRC and content comparison; exactly six HTML payload changes; 626 entries expected:',len(a.namelist()))
    print('PASS: all listed local files match handoff hashes. NOT an Android/signature/hardware test.')
    return 0
if __name__=='__main__': sys.exit(main())
