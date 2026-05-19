"""IL2CPP global-metadata.dat string literal patcher.

Format reference: Il2CppDumper / Il2CppInspector
Version 31 header (Unity 2022/2023/6):
- uint32 sanity (0xFAB11BAF)
- int32  version
- int32  stringLiteralOffset
- int32  stringLiteralSize  (size of index array: stringLiteralCount * 8 bytes; each entry = length(u32)+dataIndex(u32))
- int32  stringLiteralDataOffset
- int32  stringLiteralDataSize
- ... (more sections)
"""
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat")
OUT_DIR = Path(r"C:\Users\Ravnow\Documents\esoteric-ebb-fr\metadata_strings")
OUT_DIR.mkdir(exist_ok=True)


def parse_header(data):
    """Parse the metadata header to find string literal sections."""
    sanity, version = struct.unpack('<II', data[:8])
    assert sanity == 0xFAB11BAF, f"Bad sanity: {sanity:X}"
    print(f"Version: {version}")

    # For v29+ (Unity 2022.2+ / Unity 6):
    # offsets are at fixed positions in the header
    offsets = {}
    # The header is a series of (offset, size) int32 pairs after version
    # stringLiteral comes first
    pos = 8
    offsets['stringLiteralOffset'], offsets['stringLiteralSize'] = struct.unpack('<ii', data[pos:pos+8])
    pos += 8
    offsets['stringLiteralDataOffset'], offsets['stringLiteralDataSize'] = struct.unpack('<ii', data[pos:pos+8])
    pos += 8
    offsets['stringOffset'], offsets['stringSize'] = struct.unpack('<ii', data[pos:pos+8])
    return offsets


def list_strings(data, offsets):
    """Enumerate all stringLiteral entries: (index, length, dataOffset, string)."""
    lit_off = offsets['stringLiteralOffset']
    lit_size = offsets['stringLiteralSize']
    data_off = offsets['stringLiteralDataOffset']
    count = lit_size // 8  # each entry = 4 bytes length + 4 bytes offset
    print(f"String literals count: {count}")
    print(f"Literal index table: 0x{lit_off:X} (size 0x{lit_size:X})")
    print(f"Literal data section: 0x{data_off:X} (size 0x{offsets['stringLiteralDataSize']:X})")

    strings = []
    for i in range(count):
        entry_off = lit_off + i * 8
        length, data_index = struct.unpack('<II', data[entry_off:entry_off+8])
        abs_off = data_off + data_index
        raw = data[abs_off:abs_off+length]
        try:
            s = raw.decode('utf-8')
        except UnicodeDecodeError:
            s = raw.decode('latin-1', errors='replace')
        strings.append({
            'index': i,
            'length': length,
            'data_offset': abs_off,  # absolute file offset
            'data_index': data_index,  # offset within string data section
            'text': s,
        })
    return strings


def main():
    data = open(PATH, 'rb').read()
    print(f"File size: {len(data):,} bytes")
    offsets = parse_header(data)
    for k, v in offsets.items():
        print(f"  {k}: 0x{v:X} ({v:,})")

    strings = list_strings(data, offsets)

    # Save full dump
    with open(OUT_DIR / 'all_strings.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('index\tlength\tabs_offset\tdata_index\ttext\n')
        for s in strings:
            text_esc = s['text'].replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
            f.write(f"{s['index']}\t{s['length']}\t{s['data_offset']}\t{s['data_index']}\t{text_esc}\n")
    print(f"Dumped {len(strings)} strings to all_strings.tsv")

    # Search for our target strings
    targets = [
        'Gained experience', 'gained experience',
        'Cantrips', 'Spells', 'Cantrip', 'Spell',
        'Success', 'Failure', 'success', 'failure',
        'Hit Die', 'Hit Dice', 'short rest', 'long rest', 'Short Rest', 'Long Rest',
        ' HP', 'hp ',
        ' PE', 'PE ',
        ' xp',
        'Day ', 'DAY ',
        'DC ', 'dc ',
        'March', 'January', 'February', 'April',
        'Spend ', 'on a ',
        'You', 'you ',
        ' times', ' time',
        'Helms', 'Weaponry', 'Texts', 'Key Items', 'Food', 'Tools',
        'Clericals', 'Esoterics', 'Folk',
        'one single time', 'two times', 'three times',
    ]

    with open(OUT_DIR / 'candidates.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('index\tlength\tabs_offset\ttext\tmatched\n')
        n = 0
        for s in strings:
            for t in targets:
                if t in s['text']:
                    text_esc = s['text'].replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
                    f.write(f"{s['index']}\t{s['length']}\t{s['data_offset']}\t{text_esc}\t{t}\n")
                    n += 1
                    break
        print(f"Found {n} candidate strings matching targets")


if __name__ == '__main__':
    main()
