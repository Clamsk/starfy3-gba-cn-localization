"""Fail closed on ROMs, images, saves, archives, secrets, or undeclared files."""
import hashlib
import json
from pathlib import Path
import subprocess
import re
from bps import read_patch

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_ROOT={'README.md','README.en.md','NOTICE.md','NOTICE.en.md','release.json','.gitignore','SHA256SUMS'}
def audit(paths):
    result=[]
    for name in paths:
        path=Path(name);parts=path.parts
        allowed=name in ALLOWED_ROOT or (
            len(parts)>=2 and (
                (parts[0]=='scripts' and path.suffix=='.py') or
                (parts[0] in ('translation','engineering') and path.suffix=='.json') or
                (parts[0]=='docs' and path.suffix=='.md') or
                (parts[0]=='patches' and path.suffix=='.bps') or
                (parts[0]=='fonts' and path.suffix.lower() in ('.bdf','.txt','.md','.json')) or
                (name=='.github/workflows/audit.yml')
            ))
        if not allowed: raise ValueError(f'Unapproved public file: {name}')
        data=(ROOT/path).read_bytes()
        if len(data)>=16*1024*1024 or data[:2]==b'MZ' or data[:4]==b'PK\x03\x04':
            raise ValueError(f'Binary/archive not permitted: {name}')
        if path.suffix=='.bps':
            if len(data)>=1024*1024: raise ValueError('Patch size exceeds release gate (1 MiB)')
            _,stats=read_patch(data)
            if stats['source_bytes']!=16777216 or stats['target_bytes']!=33554432:raise ValueError('Wrong patch image sizes')
        else:
            if b'\0' in data:raise ValueError(f'Non-text payload in {name}')
            if path.suffix=='.json':json.loads(data.decode('utf-8'))
            if path.suffix=='.bdf' and not data.startswith(b'STARTFONT '):raise ValueError('Invalid public font source')
            text=data.decode('utf-8',errors='replace')
            if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}',text):
                raise ValueError(f'Secret marker in {name}')
            if '-----BEGIN '+'PRIVATE KEY-----' in text:
                raise ValueError(f'Private key marker in {name}')
        result.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    return result

if __name__=='__main__':
    git=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
    paths=[p for p in git.stdout.decode().split('\0') if p]
    if not paths:raise ValueError('No tracked release files')
    result=audit(paths)
    print(json.dumps(dict(passed=True,tracked_files=len(result),total_bytes=sum(x['bytes'] for x in result))))

