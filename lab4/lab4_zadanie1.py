import json
import math
import sys
from collections import Counter
from pathlib import Path


def create(text):
    symbols = sorted(Counter(text).keys())
    if not symbols:
        raise ValueError("Nie mozna zbudowac kodu dla pustego tekstu.")

    bits_per_symbol = max(1, math.ceil(math.log2(len(symbols))))
    code_map = {}
    reverse_map = {}

    for index, symbol in enumerate(symbols):
        code = format(index, f"0{bits_per_symbol}b")
        code_map[symbol] = code
        reverse_map[code] = symbol

    return {
        "symbols": symbols,
        "bits_per_symbol": bits_per_symbol,
        "code_map": code_map,
        "reverse_map": reverse_map,
    }


def encode(text, code):
    code_map = code["code_map"]
    bits_per_symbol = code["bits_per_symbol"]

    encoded_bits = []
    for ch in text:
        if ch not in code_map:
            raise ValueError(f"Brak znaku w kodzie: {repr(ch)}")
        encoded_bits.append(code_map[ch])

    return {
        "bits": "".join(encoded_bits),
        "bits_per_symbol": bits_per_symbol,
        "symbol_count": len(text),
    }


def decode(encoded, code):
    bits = encoded["bits"]
    bits_per_symbol = code["bits_per_symbol"]
    reverse_map = code["reverse_map"]

    if bits_per_symbol <= 0:
        raise ValueError("Niepoprawna dlugosc kodu.")
    if len(bits) % bits_per_symbol != 0:
        raise ValueError("Liczba bitow nie dzieli sie przez dlugosc kodu.")

    decoded_chars = []
    for i in range(0, len(bits), bits_per_symbol):
        chunk = bits[i:i + bits_per_symbol]
        if chunk not in reverse_map:
            raise ValueError(f"Nieznany kod binarny: {chunk}")
        decoded_chars.append(reverse_map[chunk])
    return "".join(decoded_chars)


def save(path, code, encoded):
    payload = {
        "version": 1,
        "bits_per_symbol": code["bits_per_symbol"],
        "symbols": code["symbols"],
        "symbol_count": encoded["symbol_count"],
        "bits": encoded["bits"],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def load(path):
    payload = json.loads(path.read_text(encoding="utf-8"))

    bits_per_symbol = int(payload["bits_per_symbol"])
    symbols = payload["symbols"]
    bits = payload["bits"]
    symbol_count = int(payload["symbol_count"])

    code_map = {}
    reverse_map = {}
    for index, symbol in enumerate(symbols):
        code_bits = format(index, f"0{bits_per_symbol}b")
        code_map[symbol] = code_bits
        reverse_map[code_bits] = symbol

    code = {
        "symbols": symbols,
        "bits_per_symbol": bits_per_symbol,
        "code_map": code_map,
        "reverse_map": reverse_map,
    }
    encoded = {
        "bits": bits,
        "bits_per_symbol": bits_per_symbol,
        "symbol_count": symbol_count,
    }
    return code, encoded


def compression_stats(original_text, encoded):
    original_bits = len(original_text) * 8
    compressed_bits = len(encoded["bits"])
    ratio = compressed_bits / original_bits if original_bits else 0.0
    savings = (1.0 - ratio) * 100.0 if original_bits else 0.0
    return {
        "original_bits": original_bits,
        "compressed_bits": compressed_bits,
        "ratio": ratio,
        "savings_percent": savings,
    }


def main():
    input_path = Path("norm_wiki_sample.txt")
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])

    output_path = Path("lab4_encoded.json")
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])

    if not input_path.is_file():
        print("Brak pliku:", input_path)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    if not text:
        print("Pusty plik:", input_path)
        sys.exit(1)

    code = create(text)
    encoded = encode(text, code)
    save(output_path, code, encoded)

    loaded_code, loaded_encoded = load(output_path)
    decoded_text = decode(loaded_encoded, loaded_code)

    ok = (decoded_text == text)
    stats = compression_stats(text, loaded_encoded)

    print("Plik wejsciowy:", input_path)
    print("Plik wyjsciowy:", output_path)
    print("Liczba znakow:", len(text))
    print("Rozmiar alfabetu:", len(code["symbols"]))
    print("Dlugosc kodu stalego:", code["bits_per_symbol"], "bit/znak")
    print()
    print("Poprawnosc encode/decode:", "OK" if ok else "BLAD")
    print()
    print("Rozmiary teoretyczne:")
    print("Oryginal:", stats["original_bits"], "bit")
    print("Zakodowany tekst:", stats["compressed_bits"], "bit")
    print("Wspolczynnik kompresji:", f"{stats['ratio']:.6f}")
    print("Oszczednosc:", f"{stats['savings_percent']:.2f}%")
    print()
    print("Rozmiary plikow (bajty):")
    print("Oryginal:", input_path.stat().st_size)
    print("Zapisany kod+tekst:", output_path.stat().st_size)

    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
