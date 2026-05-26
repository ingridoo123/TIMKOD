import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

MAGIC = b"LAB4F01"


def create(frequencies):
    symbols = sorted(frequencies.keys())
    symbol_count = len(symbols)
    if symbol_count == 0:
        return {}

    bit_length = max(1, math.ceil(math.log2(symbol_count)))
    code = {}
    for index, symbol in enumerate(symbols):
        code[symbol] = format(index, f"0{bit_length}b")
    return code


def encode(text, code):
    return "".join(code[ch] for ch in text)


def decode(encoded_bits, code, text_length):
    if text_length == 0:
        return ""

    inverse = {bits: symbol for symbol, bits in code.items()}
    if not inverse:
        raise ValueError("Brak kodu do dekodowania.")

    bit_length = len(next(iter(inverse)))
    required_bits = text_length * bit_length
    if len(encoded_bits) < required_bits:
        raise ValueError("Zakodowany strumien bitow jest za krotki.")

    chars = []
    for i in range(0, required_bits, bit_length):
        chunk = encoded_bits[i:i + bit_length]
        if chunk not in inverse:
            raise ValueError(f"Nieznany kod podczas dekodowania: {chunk}")
        chars.append(inverse[chunk])
    return "".join(chars)


def save(output_path, code, encoded_bits, text_length):
    if not code and text_length > 0:
        raise ValueError("Nie mozna zapisac niepustego tekstu bez kodu.")

    bit_length = len(next(iter(code.values()))) if code else 0
    symbols_sorted_by_code = [symbol for symbol, _ in sorted(code.items(), key=lambda x: x[1])]

    header = {
        "symbols": symbols_sorted_by_code,
        "bit_length": bit_length,
        "text_length": text_length,
    }
    header_bytes = json.dumps(header, ensure_ascii=True).encode("utf-8")

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
            raise ValueError("Nieprawidlowy format pliku.")

        header_len_data = f.read(4)
        if len(header_len_data) != 4:
            raise ValueError("Uszkodzony plik - brak dlugosci naglowka.")
        header_len = struct.unpack(">I", header_len_data)[0]

        header_bytes = f.read(header_len)
        if len(header_bytes) != header_len:
            raise ValueError("Uszkodzony plik - niepelny naglowek.")
        header = json.loads(header_bytes.decode("utf-8"))

        payload = f.read()

    symbols = header["symbols"]
    bit_length = int(header["bit_length"])
    text_length = int(header["text_length"])

    code = {}
    for index, symbol in enumerate(symbols):
        code[symbol] = format(index, f"0{bit_length}b")

    all_bits = "".join(format(byte, "08b") for byte in payload)
    required_bits = text_length * bit_length
    encoded_bits = all_bits[:required_bits]
    return code, encoded_bits, text_length


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


def main():
    input_path = Path("../norm_wiki_sample.txt")
    output_path = Path("encoded_lab4.bin")

    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])

    if not input_path.is_file():
        print("Brak pliku:", input_path)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    frequencies = Counter(text)
    code = create(frequencies)

    encoded_bits = encode(text, code)
    save(output_path, code, encoded_bits, len(text))
    loaded_code, loaded_bits, loaded_text_length = load(output_path)
    decoded_text = decode(loaded_bits, loaded_code, loaded_text_length)

    ok = (text == decoded_text)

    original_size, packed_size, ratio, saved = compression_stats(input_path, output_path)
    alphabet_size = len(frequencies)
    minimal_fixed_bits = max(1, math.ceil(math.log2(alphabet_size))) if alphabet_size > 0 else 0

    print("Plik wejsciowy:", input_path)
    print("Plik wyjsciowy:", output_path)
    print("Liczba znakow:", len(text))
    print("Liczba symboli alfabetu:", alphabet_size)
    print("Dlugosc kodu stalo-dlugosciowego:", minimal_fixed_bits, "bit/znak")
    print("Poprawnosc encode/decode:", "OK" if ok else "BLAD")
    print()
    print("Rozmiar oryginalu:", original_size, "B")
    print("Rozmiar spakowanego pliku:", packed_size, "B")
    if original_size > 0:
        print("Stopien kompresji (packed/original):", f"{ratio:.6f}")
        print("Oszczednosc:", f"{saved:.2f}%")


if __name__ == "__main__":
    main()
