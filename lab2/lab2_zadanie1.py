from collections import Counter
from pathlib import Path
import sys

path = Path("norm_wiki_sample.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

tekst = path.read_text(encoding="utf-8")
slowa = [s for s in tekst.split(" ") if s]

if not slowa:
    print("Brak slow w pliku.")
    sys.exit(1)

licznik = Counter(slowa)
wszystkie_slowa = len(slowa)
unikalne_slowa = len(licznik)

posortowane = sorted(licznik.items(), key=lambda x: (-x[1], x[0]))


def pokrycie_top_n(n):
    top_n = posortowane[:n]
    suma = 0
    for _, ile in top_n:
        suma += ile
    return (suma / wszystkie_slowa) * 100


pokrycie_30000 = pokrycie_top_n(30000)
pokrycie_6000 = pokrycie_top_n(6000)

print("Plik:", path)
print("Wszystkich slow:", wszystkie_slowa)
print("Unikalnych slow:", unikalne_slowa)
print()
print("Najczestsze slowa (top 30):")
print("Ranga | Slowo | Liczba | Procent")
print("------+-------+--------+--------")
for i, (slowo, ile) in enumerate(posortowane[:30], start=1):
    procent = (ile / wszystkie_slowa) * 100
    print(str(i).rjust(5), "|", slowo.ljust(20), "|", str(ile).rjust(6), "|", f"{procent:6.3f}%")

print()
print("Pokrycie slownika:")
print("Top 30000 slow:", f"{pokrycie_30000:.3f}% wszystkich slow")
print("Top  6000 slow:", f"{pokrycie_6000:.3f}% wszystkich slow")
