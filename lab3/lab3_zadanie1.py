import math
import sys
from collections import Counter
from pathlib import Path

path = Path("../lab3/sample0.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

tekst = path.read_text(encoding="utf-8")
if not tekst:
    print("Pusty plik:", path)
    sys.exit(1)

licznik = Counter(tekst)
wszystkie = sum(licznik.values())
unikalne = len(licznik)

# W przyblizeniu zerowego rzedu: 26 liter + 10 cyfr + spacja = 37 symboli
entropia_rzad_0 = math.log2(37)

entropia_empiryczna = 0.0
for _, ile in licznik.items():
    p = ile / wszystkie
    entropia_empiryczna -= p * math.log2(p)

print("Plik:", path)
print("Liczba znakow:", wszystkie)
print("Unikalnych znakow w pliku:", unikalne)
print()
print("Entropia dla przyblizenia 0. rzedu (37 rownych symboli):")
print(f"H0 = {entropia_rzad_0:.6f} bit/znak")
print()
print("Empiryczna entropia znakow z korpusu:")
print(f"H = {entropia_empiryczna:.6f} bit/znak")
