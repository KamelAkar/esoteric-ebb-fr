"""Dump a TextAsset's m_Script content by name from a Unity assets file."""
import sys
import struct
import re

assets_path = sys.argv[1]
target_name = sys.argv[2]
out_path = sys.argv[3]

data = open(assets_path, 'rb').read()

# Find name pattern: short ascii alphanum length-prefixed, followed by padding, then int32 length, then m_Script content
name_bytes = target_name.encode('utf-8')
# In Unity textasset binary: <int32 name_len><name bytes><align to 4><int32 script_len><script bytes>
# Search occurrences where name is preceded by its length
needle = struct.pack('<I', len(name_bytes)) + name_bytes
idx = 0
found = False
while True:
    pos = data.find(needle, idx)
    if pos == -1: break
    # Skip past name + align to 4
    end = pos + 4 + len(name_bytes)
    align = (4 - (end % 4)) % 4
    end += align
    # Read script length
    if end + 4 > len(data): break
    script_len = struct.unpack_from('<I', data, end)[0]
    if 100 < script_len < 5_000_000:
        script_bytes = data[end+4:end+4+script_len]
        # Sanity check: must look like JSON (start with { or [)
        if script_bytes[:1] in (b'{', b'['):
            with open(out_path, 'wb') as f:
                f.write(script_bytes)
            print(f"Found {target_name} at offset {pos}, dumped {script_len} bytes to {out_path}")
            found = True
            break
    idx = pos + 1

if not found:
    print(f"NOT FOUND: {target_name}")
    sys.exit(1)
