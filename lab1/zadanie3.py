import random
import sys
from collections import Counter
from pathlib import Path

path = Path("../norm_wiki_sample.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

tekst_korpusu = path.read_text(encoding="utf-8")
licznik = Counter(tekst_korpusu)
wszystkie = sum(licznik.values())


znaki = list(licznik.keys())
print(znaki)
wagi = list(licznik.values())


def srednia_dlugosc_slowa(tekst):

    words = []
    current_word = []
    for ch in tekst:
        if ch == " ":
            if current_word:
                words.append("".join(current_word))
                current_word = []
        else:
            current_word.append(ch)
    if not words:
        return 0.0
    suma = 0
    for s in words:
        suma += len(s)
    return suma / len(words)


srednia_korpus = srednia_dlugosc_slowa(tekst_korpusu)


dlugosc_wyjscia = 100000
ziarno = 12345
rng = random.Random(ziarno)


wygenerowany = "".join(rng.choices(znaki, weights=wagi, k=dlugosc_wyjscia))

srednia_model = srednia_dlugosc_slowa(wygenerowany)

print("Plik:", path)
print("Znaki w pliki:", wszystkie)
print("Unikalnych znakow (alfabet losowania):", len(znaki))
print()
print("Dlugosc wygenerowanego tekstu:", len(wygenerowany), "znakow")
print("Ziarno RNG:", ziarno)
print()
print("Srednia dlugosc slowa w korpusie:     ", f"{srednia_korpus:.4f}")
print("Srednia dlugosc slowa w przyblizeniu: ", f"{srednia_model:.4f}")
print()
roznica = srednia_model - srednia_korpus
print("Roznica (model - korpus):", f"{roznica:+.4f}")
print()
print(
    "Przyblizenie 1. rzedu kopiuje czestotliwosci liter, ale slowa sa "
    "losowymi ciagami znakow - dlatego srednia dlugosc slowa zwykle "
    "nie zbiega do tej z prawdziwego tekstu."
)
