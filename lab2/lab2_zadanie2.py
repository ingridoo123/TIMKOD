import random
import sys
from collections import Counter
from pathlib import Path

path = Path("norm_wiki_sample.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

ile_slow_generowac = 200
if len(sys.argv) > 2:
    ile_slow_generowac = int(sys.argv[2])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

tekst = path.read_text(encoding="utf-8")
slowa = [s for s in tekst.split(" ") if s]

if not slowa:
    print("Brak slow w pliku.")
    sys.exit(1)

licznik = Counter(slowa)
slownik = list(licznik.keys())
wagi = list(licznik.values())

ziarno = 12345
rng = random.Random(ziarno)

wygenerowane = rng.choices(slownik, weights=wagi, k=ile_slow_generowac)
tekst_wynik = " ".join(wygenerowane)

print("Plik:", path)
print("Liczba slow w korpusie:", len(slowa))
print("Liczba unikalnych slow:", len(slownik))
print("Liczba wygenerowanych slow:", ile_slow_generowac)
print("Ziarno RNG:", ziarno)
print()
print("Przyblizenie pierwszego rzedu na slowach:")
print(tekst_wynik)
