"""Edit Chinese runs; recover all controls/original data from the user's local image."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_block(image, base):
    if image[base:base+8] != b'MESGbmg1': raise ValueError('Invalid BMG address')
    length, count = struct.unpack_from('>II', image, base+8)
    if base + length > len(image): raise ValueError('BMG exceeds image')
    sections = []; pos = base+32
    for _ in range(count):
        size = struct.unpack_from('>I', image, pos+4)[0]
        if size < 8 or pos+size > base+length: raise ValueError('Invalid BMG section')
        sections.append(bytearray(image[pos:pos+size])); pos += size
    info = next(s for s in sections if s[:4] == b'INF1')
    data = next(s for s in sections if s[:4] == b'DAT1')
    number, stride = struct.unpack_from('>HH', info, 8)
    offsets = [struct.unpack_from('>I', info, 16+i*stride)[0] for i in range(number)]
    entries = [bytes(data[8+o:8+(offsets[i+1] if i+1<number else len(data)-8)]) for i,o in enumerate(offsets)]
    return dict(header=bytearray(image[base:base+32]), sections=sections, stride=stride, entries=entries)

def tokenize(raw):
    tokens=[]; pos=0; start=0
    while pos<len(raw):
        if raw[pos] in (0,26):
            if pos>start: tokens.append(('text',raw[start:pos]))
            if raw[pos]==0:
                tokens.append(('end',b'\0')); return tokens
            if pos+1>=len(raw): raise ValueError('Truncated control')
            size=raw[pos+1]
            if size<5 or pos+size>len(raw): raise ValueError('Invalid control length')
            packet=raw[pos:pos+size]
            kind='name' if packet[2:5]==bytes.fromhex('020001') and size>6 else 'control'
            tokens.append((kind,packet)); pos+=size; start=pos
        else: pos+=1
    raise ValueError('No BMG terminator')

def decode(raw, reverse):
    chars=[];pos=0
    while pos<len(raw):
        if raw[pos]<128: chars.append(chr(raw[pos]));pos+=1
        elif raw[pos:pos+2].hex() in reverse:
            chars.append(reverse[raw[pos:pos+2].hex()]);pos+=2
        elif 0xa1<=raw[pos]<=0xdf: chars.append(raw[pos:pos+1].decode('cp932'));pos+=1
        else: chars.append(raw[pos:pos+2].decode('cp932'));pos+=2
    return ''.join(chars)

def encode(text, codes):
    result=bytearray()
    for c in text:
        if c in codes: result.extend(bytes.fromhex(codes[c]))
        elif ord(c)<128 and (ord(c)>=32 or c=='\n'): result.append(ord(c))
        elif c in '①②③④⑤⑥⑦⑧': result.extend(c.encode('cp932'))
        else: raise ValueError(f'Character not in frozen font encoding: {c!r}')
    return result

def apply_edits(image, edits):
    reference=json.loads((ROOT/'translation/messages.zh.json').read_text(encoding='utf-8'))
    if set(edits)!=set(reference): raise ValueError('Message keys must match the baseline')
    codes=json.loads((ROOT/'translation/encoding.json').read_text(encoding='utf-8'))
    layout=json.loads((ROOT/'engineering/bmg_layout.json').read_text(encoding='utf-8'))
    output=bytearray(image); cursor=0x1c00000; changed=0
    for record in layout:
        block=read_block(image,record['base']);revised=[];dirty=False
        for index,raw in enumerate(block['entries']):
            key=f'{record["block"]}:{index}'; current=reference[key]; proposed=edits[key]
            if len(current)!=len(proposed): raise ValueError(f'Control boundaries changed: {key}')
            tokens=tokenize(raw); parts=[]
            if len(current)!=len(tokens): raise ValueError(f'Token count mismatch: {key}')
            for slot,((kind,packet),old,new) in enumerate(zip(tokens,current,proposed)):
                if old.get('slot')!=slot or new.get('slot')!=slot or old['kind']!=new['kind']:
                    raise ValueError(f'Token identity changed: {key}/{slot}')
                if 'zh' not in old:
                    if old!=new: raise ValueError(f'Preserved boundary edited: {key}/{slot}')
                    parts.append(packet);continue
                if set(new)!=set(old) or not isinstance(new['zh'],str): raise ValueError('Invalid text record')
                if new['zh']==old['zh']: parts.append(packet);continue
                dirty=True; data=encode(new['zh'],codes)
                if record['block']==26 and (len(new['zh'].split('\n'))>5 or any(len(line)>7 for line in new['zh'].split('\n'))):
                    raise ValueError('Item descriptions must fit 7 columns x 5 rows')
                if kind=='name':
                    data=bytearray(packet[:6])+data
                    if len(data)>255: raise ValueError('Speaker name too long')
                    data[1]=len(data)
                parts.append(data)
            revised.append(b''.join(parts))
        if not dirty: continue
        payload=bytearray(b'\0');offsets=[]
        for raw in revised: offsets.append(len(payload));payload.extend(raw)
        sections=[]
        for section in block['sections']:
            part=bytearray(section)
            if part[:4]==b'INF1':
                for index,offset in enumerate(offsets):struct.pack_into('>I',part,16+index*block['stride'],offset)
            elif part[:4]==b'DAT1':
                part=bytearray(b'DAT1\0\0\0\0')+payload;part.extend(bytes((-len(part))%32));struct.pack_into('>I',part,4,len(part))
            sections.append(part)
        rebuilt=block['header']+b''.join(sections);struct.pack_into('>I',rebuilt,8,len(rebuilt))
        if cursor+len(rebuilt)>len(output) or any(b!=255 for b in image[cursor:cursor+len(rebuilt)]):
            raise ValueError('Insufficient reserved BMG editing space')
        output[cursor:cursor+len(rebuilt)]=rebuilt
        for ptr in record['pointers']:
            if struct.unpack_from('<I',output,ptr)[0]!=record['base']+0x8000000: raise ValueError('BMG pointer mismatch')
            struct.pack_into('<I',output,ptr,cursor+0x8000000)
        cursor=(cursor+len(rebuilt)+31)&~31;changed+=1
    return output,changed

