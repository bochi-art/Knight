import re, lzma, sys
from xml.etree import ElementTree as ET

def decode_svg_to_text(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    uses = []
    for elem in root.iter():
        if isinstance(elem.tag, str) and elem.tag.endswith("use"):
            transform = elem.attrib.get("transform") or ""
            m = re.search(r"scale\s*\(\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)", transform)
            if m:
                sx = float(m.group(1))
                sy = float(m.group(2))
                uses.append((sx, sy))

    pairs = len(uses) // 2
    selected = [uses[i*2] for i in range(pairs)]

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    symbols = []
    for sx, sy in selected:
        q7 = int(round(127 * ((sx - 1.0)/0.12 + 0.5)))
        q7 = clamp(q7, 0, 127)
        q6 = int(round(63 * ((sy - 1.0)/0.10 + 0.5)))
        q6 = clamp(q6, 0, 63)
        sym = (q6 << 7) | q7
        symbols.append(sym)

    bits = []
    for sym in symbols:
        for bitpos in range(12, -1, -1):
            bits.append((sym >> bitpos) & 1)
    bits.append(0)
    while len(bits) % 8 != 0:
        bits.append(0)

    byte_arr = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for j in range(8):
            b = (b << 1) | bits[i + j]
        byte_arr.append(b)
    if len(byte_arr) > 0:
        byte_arr = byte_arr[:-1]

    decompressed = lzma.decompress(byte_arr)
    return decompressed.decode("utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python The_Knight_in_the_Panthers_Skin.py input.svg")
        sys.exit(1)
    svg_file = sys.argv[1]
    text = decode_svg_to_text(svg_file)
    out_path = "The_Knight_in_the_Panthers_Skin.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Decoded output from your SVG: Download The_Knight_in_the_Panthers_Skin.txt")
