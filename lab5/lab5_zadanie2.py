import heapq
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

# Unikalny identyfikator formatu pliku dla Lab 5 (Huffman)
MAGIC = b"LAB5F02"


def calculate_entropy(text):
    if not text:
        return 0.0
    frequencies = Counter(text)
    total_chars = len(text)
    entropy = 0.0
    for count in frequencies.values():
        p = count / total_chars
        entropy -= p * math.log2(p)
    return entropy


def create_huffman_code(frequencies):
    if not frequencies:
        return {}

    # Przypadek szczególny: alfabet składa się tylko z 1 znaku
    if len(frequencies) == 1:
        char = list(frequencies.keys())[0]
        return {char: "0"}

    # Kolejka priorytetowa przechowuje elementy w formacie:
    # (częstość, licznik_unikalny, (znak, lewy_syn, prawy_syn))
    # Licznik_unikalny (counter) zapobiega błędom porównywania krotek o tej samej częstości.
    heap = []
    counter = 0
    for char, freq in frequencies.items():
        heapq.heappush(heap, (freq, counter, (char, None, None)))
        counter += 1

    while len(heap) > 1:
        freq1, _, node1 = heapq.heappop(heap)
        freq2, _, node2 = heapq.heappop(heap)
        parent = (None, node1, node2)
        heapq.heappush(heap, (freq1 + freq2, counter, parent))
        counter += 1

    _, _, root = heap[0]

    code = {}

    def traverse(node, current_code):
        char, left, right = node
        if char is not None:
            code[char] = current_code
            return
        if left is not None:
            traverse(left, current_code + "0")
        if right is not None:
            traverse(right, current_code + "1")

    traverse(root, "")
    return code


def calculate_average_code_length(frequencies, code):
    total_chars = sum(frequencies.values())
    if total_chars == 0:
        return 0.0
    avg_length = 0.0
    for char, count in frequencies.items():
        p = count / total_chars
        avg_length += p * len(code[char])
    return avg_length


def encode(text, code):
    return "".join(code[char] for char in text)


def decode(encoded_bits, code, text_length):
    if text_length == 0 or not encoded_bits:
        return ""

    # Odwrócenie słownika kodów dla szybkiego wyszukiwania
    inverse = {bits: char for char, bits in code.items()}
    if not inverse:
        raise ValueError("Brak kodów do dekodowania.")

    decoded_chars = []
    current_bits = ""
    for bit in encoded_bits:
        current_bits += bit
        if current_bits in inverse:
            decoded_chars.append(inverse[current_bits])
            current_bits = ""

            # Bezpiecznik: jeśli odtworzyliśmy już cały oryginalny tekst
            if len(decoded_chars) == text_length:
                break

    return "".join(decoded_chars)


def save(output_path, code, encoded_bits, text_length):
    header = {
        "code": code,
        "text_length": text_length,
        "total_bits": len(encoded_bits)
    }
    header_bytes = json.dumps(header, ensure_ascii=True).encode("utf-8")

    # Dopełnienie do pełnych bajtów
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
            raise ValueError("Nieprawidłowy format pliku (brak sygnatury MAGIC).")

        header_len_data = f.read(4)
        if len(header_len_data) != 4:
            raise ValueError("Uszkodzony nagłówek pliku.")
        header_len = struct.unpack(">I", header_len_data)[0]

        header_bytes = f.read(header_len)
        if len(header_bytes) != header_len:
            raise ValueError("Niekompletne metadane nagłówka.")
        header = json.loads(header_bytes.decode("utf-8"))

        payload = f.read()

    code = header["code"]
    text_length = header["text_length"]
    total_bits = header["total_bits"]

    # Konwersja bajtów z powrotem na ciąg bitów tekstowych
    all_bits = "".join(format(byte, "08b") for byte in payload)
    encoded_bits = all_bits[:total_bits]

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
    # Domyślne ścieżki do plików
    input_path = Path("../norm_wiki_sample.txt")
    if not input_path.is_file():
        input_path = Path("norm_wiki_sample.txt")

    output_path = Path("encoded_huffman.bin")

    # Obsługa argumentów linii komend
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])

    if not input_path.is_file():
        print(f"Brak pliku: {input_path}")
        sys.exit(1)

    # Wczytanie pliku
    text = input_path.read_text(encoding="utf-8")
    if not text:
        print("Plik jest pusty.")
        sys.exit(0)

    # 1. Zbudowanie słownika częstości i kodów Huffmana
    frequencies = Counter(text)
    code = create_huffman_code(frequencies)

    # 2. Kodowanie, zapis, odczyt i dekodowanie
    encoded_bits = encode(text, code)
    save(output_path, code, encoded_bits, len(text))

    loaded_code, loaded_bits, loaded_text_length = load(output_path)
    decoded_text = decode(loaded_bits, loaded_code, loaded_text_length)

    # Weryfikacja poprawności dekodowania
    is_correct = (text == decoded_text)

    # 3. Wyliczenie statystyk
    entropy = calculate_entropy(text)

    # Z Lab 4 (kodowanie stałodługościowe)
    alphabet_size = len(frequencies)
    fixed_bit_length = max(1, math.ceil(math.log2(alphabet_size))) if alphabet_size > 0 else 0
    eff_fixed = (entropy / fixed_bit_length * 100.0) if fixed_bit_length > 0 else 0.0

    # Z Lab 5 (kodowanie Huffmana)
    huffman_avg_length = calculate_average_code_length(frequencies, code)
    eff_huffman = (entropy / huffman_avg_length * 100.0) if huffman_avg_length > 0 else 0.0

    original_size, packed_size, ratio, saved = compression_stats(input_path, output_path)

    # 4. Wypisanie wyników
    print("=================== ZADANIE 2: KODOWANIE HUFFMANA ===================")
    print(f"Plik wejściowy:                  {input_path.resolve()}")
    print(f"Plik skompresowany:              {output_path.resolve()}")
    print(f"Liczba znaków w tekście:         {len(text)}")
    print(f"Rozmiar alfabetu (unikalne zn.): {alphabet_size}")
    print(f"Entropia źródła (H):             {entropy:.6f} bitów/znak")
    print()
    print("--- PORÓWNANIE METOD KODOWANIA ---")
    print(f"Długość kodu stałego (L_fixed):  {fixed_bit_length} bitów/znak")
    print(f"Średnia dł. kodu Huffmana (L_h): {huffman_avg_length:.6f} bitów/znak")
    print(f"Efektywność kodu stałego:        {eff_fixed:.2f}%")
    print(f"Efektywność kodu Huffmana:       {eff_huffman:.2f}%")
    print()
    print("--- WERYFIKACJA POPRAWNOŚCI ---")
    print(f"Czy dekompresja działa poprawnie: {'OK' if is_correct else 'BŁĄD'}")
    print()
    print("--- ROZMIARY I STOPIEŃ KOMPRESJI ---")
    print(f"Rozmiar oryginalny:              {original_size} B")
    print(f"Rozmiar skompresowany (z nagł.):  {packed_size} B")
    print(f"Stopień kompresji (bin/txt):     {ratio:.6f}")
    print(f"Oszczędność miejsca:             {saved:.2f}%")
    print("=====================================================================")


if __name__ == "__main__":
    main()
