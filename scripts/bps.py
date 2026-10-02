"""BPS reader with strict checksums and bounds. Python standard library only."""
import struct
import zlib

def crc(data):
    return zlib.crc32(data) & 0xffffffff

def read_patch(patch, source=None):
    if len(patch) < 19 or patch[:4] != b'BPS1':
        raise ValueError('Not a BPS patch')
    source_crc, target_crc, patch_crc = struct.unpack('<III', patch[-12:])
    if crc(patch[:-4]) != patch_crc:
        raise ValueError('Patch CRC32 mismatch')
    pos = 4
    def number():
        nonlocal pos
        value, shift = 0, 1
        while True:
            if pos >= len(patch) - 12:
                raise ValueError('Truncated BPS integer')
            byte = patch[pos]; pos += 1
            value += (byte & 127) * shift
            if byte & 128:
                return value
            shift <<= 7; value += shift
            if shift > 1 << 63:
                raise ValueError('Oversized BPS integer')
    source_size, target_size, metadata_size = number(), number(), number()
    if pos + metadata_size > len(patch) - 12 or target_size > 64 * 1024 * 1024:
        raise ValueError('Invalid BPS size')
    pos += metadata_size
    if source is not None and (len(source) != source_size or crc(source) != source_crc):
        raise ValueError('Wrong original image: size/CRC32 mismatch')
    output = bytearray() if source is not None else None
    cursor, source_relative, target_relative = 0, 0, 0
    counts = [0] * 4; sizes = [0] * 4
    while cursor < target_size:
        command = number(); kind = command & 3; length = (command >> 2) + 1
        if cursor + length > target_size:
            raise ValueError('BPS output overrun')
        counts[kind] += 1; sizes[kind] += length
        if kind == 0:
            if cursor + length > source_size:
                raise ValueError('BPS SourceRead overrun')
            if output is not None: output.extend(source[cursor:cursor + length])
        elif kind == 1:
            if pos + length > len(patch) - 12:
                raise ValueError('Truncated BPS literal')
            if output is not None: output.extend(patch[pos:pos + length])
            pos += length
        else:
            delta = number(); delta = -(delta >> 1) if delta & 1 else delta >> 1
            if kind == 2:
                source_relative += delta
                if source_relative < 0 or source_relative + length > source_size:
                    raise ValueError('BPS SourceCopy overrun')
                if output is not None: output.extend(source[source_relative:source_relative + length])
                source_relative += length
            else:
                target_relative += delta
                if not 0 <= target_relative < cursor:
                    raise ValueError('Invalid BPS TargetCopy reference')
                if output is not None:
                    for _ in range(length):
                        output.append(output[target_relative]); target_relative += 1
                else: target_relative += length
        cursor += length
    if pos != len(patch) - 12:
        raise ValueError('Unexpected BPS trailing data')
    if output is not None and crc(output) != target_crc:
        raise ValueError('Target CRC32 mismatch')
    stats = dict(source_bytes=source_size, target_bytes=target_size,
                 source_crc32=f'{source_crc:08X}', target_crc32=f'{target_crc:08X}',
                 patch_crc32=f'{patch_crc:08X}', action_counts=counts,
                 action_bytes=dict(zip(['SourceRead','TargetRead','SourceCopy','TargetCopy'], sizes)),
                 embedded_literal_bytes=sizes[1])
    return output, stats

