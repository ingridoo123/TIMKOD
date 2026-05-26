import sys
from collections import Counter, defaultdict
from pathlib import Path

path = Path("../norm_romeo.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

tekst = path.read_text(encoding="utf-8")

if len(tekst) < 2:
    print("Za krotki tekst na bigramy.")
    sys.exit(1)

licznik_znakow = Counter(tekst)


posortowane = sorted(licznik_znakow.items(), key=lambda x: (-x[1], x[0]))
pierwszy = posortowane[0][0]
drugi = posortowane[1][0]

after = defaultdict(Counter)
for k in range(len(tekst) - 1):
    i = tekst[k]
    j = tekst[k + 1]
    after[i][j] += 1
print(after)

def pokaz(i, nazwa):
    print("=== Znak", nazwa, "(", repr(i), ") ===")
    c = after[i]
    razem = sum(c.values())
    if razem == 0:
        print("Brak przejsc (niemozliwe dla znaku z korpusu z bigramami).")
        return
    print("Lacznie wystapien tego znaku z nastepnikiem:", razem)
    print("j (nastepny) | liczba | P(j|i)")
    print("-------------+--------+--------")
    for j in sorted(c.keys()):
        cnt = c[j]
        p = cnt / razem
        print(" ", repr(j).rjust(11), "|", str(cnt).rjust(6), "|", f"{p:.6f}")
    print()


print("Plik:", path)
print("Dlugosc tekstu:", len(tekst), "znakow")
print()
print("1. najczestszy znak:", repr(pierwszy), "liczba:", licznik_znakow[pierwszy])
print("2. najczestszy znak:", repr(drugi), "liczba:", licznik_znakow[drugi])
print()

pokaz(pierwszy, "1.")
pokaz(drugi, "2.")

print(
    "Wniosek: rozklad nastepnego znaku zalezy od i - np. po spacji czesto "
    "litera, a rozklad P(j) bez warunku (zad. 2) bylby inny. To uzasadnia "
    "zrodlo Markova wyzszego rzedu niz 1."
)
