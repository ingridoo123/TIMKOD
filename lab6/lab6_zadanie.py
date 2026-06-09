import json
import math
import struct
import sys
from pathlib import Path

MAGIC = b"LAB6LZW"

DICT_LIMITS = {
    "none": None,
    "4096": 4096,
    "262144": 262144,
}


def initial_code_width(max_dict_size):
    if max_dict_size is None:
        return 9
    return max(9, math.ceil(math.log2(max_dict_size)))


def compress(data, max_dict_size=None):
    if not data:
        return []

    dictionary = {bytes([i]): i for i in range(256)}
    next_code = 256
    w = bytes([data[0]])
    codes = []

    for i in range(1, len(data)):
        c = bytes([data[i]])
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            codes.append(dictionary[w])
            if max_dict_size is None or next_code < max_dict_size:
                dictionary[wc] = next_code
                next_code += 1
            w = c

    codes.append(dictionary[w])
    return codes


def decompress(codes, max_dict_size=None):
    if not codes:
        return b""

    dictionary = {i: bytes([i]) for i in range(256)}
    next_code = 256

    old = codes[0]
    result = bytearray(dictionary[old])

    for new in codes[1:]:
        if new in dictionary:
            entry = dictionary[new]
        elif new == next_code:
            entry = dictionary[old] + bytes([dictionary[old][0]])
        else:
            raise ValueError(f"Nieznany kod LZW podczas dekompresji: {new}")

        result.extend(entry)

        if max_dict_size is None or next_code < max_dict_size:
            dictionary[next_code] = dictionary[old] + bytes([entry[0]])
            next_code += 1

        old = new

    return bytes(result)


def pack_codes(codes, max_dict_size=None):
    if not codes:
        return ""

    width = initial_code_width(max_dict_size)
    next_code = 256
    bits = []

    if codes[0] >= (1 << width):
        raise ValueError(f"Kod {codes[0]} nie miesci sie w {width} bitach.")
    bits.append(format(codes[0], f"0{width}b"))

    for code in codes[1:]:
        if max_dict_size is None and next_code == (1 << width):
            width += 1
        if code >= (1 << width):
            raise ValueError(f"Kod {code} nie miesci sie w {width} bitach.")
        bits.append(format(code, f"0{width}b"))
        if max_dict_size is None or next_code < max_dict_size:
            next_code += 1

    return "".join(bits)


def unpack_codes(bit_string, code_count, max_dict_size=None):
    if code_count == 0:
        return []

    width = initial_code_width(max_dict_size)
    next_code = 256
    codes = []
    pos = 0

    if pos + width > len(bit_string):
        raise ValueError("Za krotki strumien bitow LZW.")
    codes.append(int(bit_string[pos:pos + width], 2))
    pos += width

    for _ in range(code_count - 1):
        if max_dict_size is None and next_code == (1 << width):
            width += 1
        if pos + width > len(bit_string):
            raise ValueError("Za krotki strumien bitow LZW.")
        codes.append(int(bit_string[pos:pos + width], 2))
        pos += width
        if max_dict_size is None or next_code < max_dict_size:
            next_code += 1

    return codes


def save(output_path, codes, original_size, max_dict_size=None):
    header = {
        "max_dict_size": max_dict_size,
        "original_size": original_size,
        "code_count": len(codes),
    }
    header_bytes = json.dumps(header, ensure_ascii=True).encode("utf-8")

    encoded_bits = pack_codes(codes, max_dict_size)
    padding = (8 - (len(encoded_bits) % 8)) % 8
    padded_bits = encoded_bits + ("0" * padding)

    payload = bytearray()
    for i in range(0, len(padded_bits), 8):
        payload.append(int(padded_bits[i:i + 8], 2))

    with output_path.open("wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">I", len(header_bytes)))
        f.write(header_bytes)
        f.write(bytes(payload))


def load(input_path):
    with input_path.open("rb") as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Nieprawidlowy format pliku (brak sygnatury MAGIC).")

        header_len_data = f.read(4)
        if len(header_len_data) != 4:
            raise ValueError("Uszkodzony naglowek pliku.")
        header_len = struct.unpack(">I", header_len_data)[0]

        header_bytes = f.read(header_len)
        if len(header_bytes) != header_len:
            raise ValueError("Niekompletne metadane naglowka.")
        header = json.loads(header_bytes.decode("utf-8"))

        payload = f.read()

    max_dict_size = header["max_dict_size"]
    original_size = int(header["original_size"])
    code_count = int(header["code_count"])

    all_bits = "".join(format(byte, "08b") for byte in payload)
    used_bits = 0
    if code_count > 0:
        width = initial_code_width(max_dict_size)
        next_code = 256
        used_bits += width
        for _ in range(code_count - 1):
            if max_dict_size is None and next_code == (1 << width):
                width += 1
            used_bits += width
            if max_dict_size is None or next_code < max_dict_size:
                next_code += 1

    encoded_bits = all_bits[:used_bits]
    codes = unpack_codes(encoded_bits, code_count, max_dict_size)
    return codes, original_size, max_dict_size


def compression_stats(original_path, packed_path):
    original_size = original_path.stat().st_size
    packed_size = packed_path.stat().st_size
    if original_size == 0:
        ratio = 0.0
        saved = 0.0
    else:
        ratio = packed_size / original_size
        saved = (1.0 - ratio) * 100.0
    return original_size, packed_size, ratio, saved


def dict_limit_label(max_dict_size):
    if max_dict_size is None:
        return "bez limitu"
    return str(max_dict_size)


def process_file(input_path, output_dir, max_dict_size):
    data = input_path.read_bytes()
    codes = compress(data, max_dict_size)

    limit_name = "unlimited" if max_dict_size is None else str(max_dict_size)
    output_path = output_dir / f"{input_path.stem}_lzw_{limit_name}.bin"

    save(output_path, codes, len(data), max_dict_size)
    loaded_codes, original_size, loaded_limit = load(output_path)
    decoded = decompress(loaded_codes, loaded_limit)

    ok = (data == decoded)
    original_size_stat, packed_size, ratio, saved = compression_stats(input_path, output_path)

    return {
        "output_path": output_path,
        "codes": len(codes),
        "ok": ok,
        "original_size": original_size_stat,
        "packed_size": packed_size,
        "ratio": ratio,
        "saved": saved,
    }


def main():
    default_files = [
        Path("norm_wiki_sample.txt"),
        Path("wiki_sample.txt"),
        Path("lena.bmp"),
    ]

    if len(sys.argv) > 1:
        input_files = [Path(sys.argv[1])]
    else:
        input_files = default_files

    output_dir = Path("compressed")
    output_dir.mkdir(exist_ok=True)

    missing = [path for path in input_files if not path.is_file()]
    if missing:
        for path in missing:
            print("Brak pliku:", path)
        print("Uzycie: python lab6_zadanie.py [sciezka_do_pliku]")
        sys.exit(1)

    print("==================== ZADANIE: KOMPRESJA LZW ====================")

    for input_path in input_files:
        print()
        print(f"Plik wejsciowy: {input_path.resolve()}")
        print(f"Rozmiar oryginalu: {input_path.stat().st_size} B")
        print()
        print("Limit slownika | Rozmiar skomp. | Stopien kompr. | Oszczednosc | Poprawnosc")
        print("---------------+----------------+----------------+-------------+-----------")

        for limit_name, max_dict_size in DICT_LIMITS.items():
            result = process_file(input_path, output_dir, max_dict_size)
            status = "OK" if result["ok"] else "BLAD"
            print(
                f"{dict_limit_label(max_dict_size):14} | "
                f"{result['packed_size']:>14} B | "
                f"{result['ratio']:>14.6f} | "
                f"{result['saved']:>10.2f}% | "
                f"{status:>9}"
            )
            print(f"  -> {result['output_path'].name} ({result['codes']} kodow)")

    print()
    print("================================================================")


if __name__ == "__main__":
    main()
