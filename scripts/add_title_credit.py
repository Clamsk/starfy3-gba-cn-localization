"""Reproduce v25 from a locally supplied v24 image and original signature pixels."""
import argparse, hashlib, json, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def decompress(data,at):
    if data[at]!=0x10:raise ValueError('Expected a BIOS LZ77 bank')
    size=int.from_bytes(data[at+1:at+4],'little');p=at+4;out=bytearray()
    while len(out)<size:
        flags=data[p];p+=1
        for bit in range(7,-1,-1):
            if len(out)>=size:break
            if flags&(1<<bit):
                a,b=data[p:p+2];p+=2;n=(a>>4)+3;distance=((a&15)<<8|b)+1
                if distance>len(out):raise ValueError('Invalid LZ reference')
                for _ in range(n):
                    if len(out)<size:out.append(out[-distance])
            else:out.append(data[p]);p+=1
    return out

def rebuild(base):
    credit=json.loads((ROOT/'engineering/title_credit_v25.json').read_text(encoding='utf-8'))
    if hashlib.sha256(base).hexdigest()!=credit['base_sha256']:
        raise ValueError('This optional generator requires the specified local v24 image')
    ptr=credit['bank_pointer'];layout=credit['layout'];destination=credit['destination']
    raw=decompress(base,struct.unpack_from('<I',base,ptr)[0]-0x8000000)
    pixels=credit['pixels'];slots=credit['slots']
    if len(pixels)!=16 or any(len(row)!=160 or any(not 0<=v<16 for v in row) for row in pixels):
        raise ValueError('Invalid original signature bitmap')
    for j,slot in enumerate(slots):
        if any(raw[slot*32:(slot+8)*32]):raise ValueError('Reserved signature tiles are not blank')
        for y in range(16):
            for x in range(32):
                at=(slot+y//8*4+x//8)*32+y%8*4+x%8//2
                raw[at]|=pixels[y][j*32+x]<<(4*(x%2))
    encoded=bytearray(b'\x10'+len(raw).to_bytes(3,'little'))
    # Literal packets are safe for the BIOS VRAM decompressor.
    for p in range(0,len(raw),8):encoded.append(0);encoded.extend(raw[p:p+8])
    if any(v!=255 for v in base[destination:destination+len(encoded)]):
        raise ValueError('Reserved ROM allocation is occupied')
    out=bytearray(base);out[destination:destination+len(encoded)]=encoded
    struct.pack_into('<I',out,ptr,0x8000000+destination)
    for frame in credit['frames']:
        start=layout+2*struct.unpack_from('<H',base,layout+12+frame*2)[0]
        for j,slot in enumerate(slots):
            struct.pack_into('<3H',out,start+2+(6+j)*6,0x4000|((-48)&255),
                             0x8000|((-80+j*32)&511),slot)
    if hashlib.sha256(out).hexdigest()!=credit['target_sha256']:
        raise ValueError('Reconstructed v25 checksum mismatch')
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Output must be a new local file')
    out=rebuild(a.base.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('xb') as f:f.write(out)
    print(json.dumps({'sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'local_only':True}))

if __name__=='__main__':main()
