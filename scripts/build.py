"""Offline reproduction of v24; never downloads an original image."""
import argparse
import hashlib
import json
from pathlib import Path
from bps import read_patch

ROOT = Path(__file__).resolve().parents[1]

def baseline(source):
    manifest = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
    if hashlib.sha256(source).hexdigest() != manifest['source']['sha256']:
        raise ValueError('Wrong original image SHA256; please supply the specified Rev0 image')
    patch = (ROOT / manifest['patch']['path']).read_bytes()
    if hashlib.sha256(patch).hexdigest() != manifest['patch']['sha256']:
        raise ValueError('Patch SHA256 mismatch')
    output, _ = read_patch(patch, source)
    if hashlib.sha256(output).hexdigest() != manifest['target']['sha256']:
        raise ValueError('v24 output SHA256 mismatch')
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--edits', type=Path, help='Edited Chinese-only messages JSON')
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve() or args.output.exists():
        raise ValueError('Output must be a new file; existing images/saves are never overwritten')
    output = baseline(args.source.read_bytes())
    changes = 0
    if args.edits:
        from script_editor import apply_edits
        output, changes = apply_edits(output, json.loads(args.edits.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as f: f.write(output)
    print(json.dumps(dict(bytes=len(output), sha256=hashlib.sha256(output).hexdigest(),
                          edited_blocks=changes, local_only=True)))

if __name__ == '__main__': main()

