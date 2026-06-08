import math
import sys
from collections import Counter
from pathlib import Path


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


def main():
    # Domyślny plik testowy szukany w katalogu wyżej (projektu) lub bieżącym
    input_path = Path("../norm_wiki_sample.txt")
    if not input_path.is_file():
        input_path = Path("norm_wiki_sample.txt")

    # Obsługa argumentów linii komend
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])

    if not input_path.is_file():
        print(f"Brak pliku: {input_path}")
        print("Możesz przekazać ścieżkę do pliku jako argument, np.:")
        print("  python lab5_zadanie1.py ścieżka_do_pliku.txt")
        sys.exit(1)

    try:
        text = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("Błąd kodowania pliku. Upewnij się, że plik ma kodowanie UTF-8.")
        sys.exit(1)

    char_counts = Counter(text)
    total_chars = len(text)
    alphabet_size = len(char_counts)

    if total_chars == 0:
        print("Plik jest pusty.")
        sys.exit(0)

    # Entropia źródła (H)
    entropy = calculate_entropy(text)

    # Długość słowa kodowego dla kodowania stałodługościowego (L)
    # L_fixed = ceil(log2(N))
    fixed_bit_length = max(1, math.ceil(math.log2(alphabet_size))) if alphabet_size > 0 else 0

    # Efektywność kodowania stałodługościowego (Eff = H / L)
    efficiency = (entropy / fixed_bit_length * 100.0) if fixed_bit_length > 0 else 0.0

    print("=================== ZADANIE 1: STATYSTYKI KODOWANIA STAŁODEUGOŚCIOWEGO ===================")
    print(f"Plik wejściowy:                  {input_path.resolve()}")
    print(f"Liczba znaków w tekście:         {total_chars}")
    print(f"Liczba unikalnych znaków (N):    {alphabet_size}")
    print(f"Entropia źródła (H):             {entropy:.6f} bitów/znak")
    print(f"Długość słowa kodowego (L_fixed):{fixed_bit_length} bitów/znak")
    print(f"Efektywność kodowania (Eff):     {efficiency:.2f}%")
    print("==========================================================================================")


if __name__ == "__main__":
    main()
