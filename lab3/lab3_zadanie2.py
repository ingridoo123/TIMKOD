import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def wczytaj_znaki(path):
    return path.read_text(encoding="utf-8")


def tokeny_slowa(tekst):
    return [s for s in tekst.split(" ") if s]


def entropia_podstawowa(tokeny):
    if not tokeny:
        return 0.0
    c = Counter(tokeny)
    n = len(tokeny)
    h = 0.0
    for _, ile in c.items():
        p = ile / n
        h -= p * math.log2(p)
    return h


def entropia_warunkowa(tokeny, rzad):
    if rzad < 1:
        return entropia_podstawowa(tokeny)
    if len(tokeny) <= rzad:
        return 0.0

    przejscia = defaultdict(Counter)
    for i in range(len(tokeny) - rzad):
        kontekst = tuple(tokeny[i:i + rzad])
        nastepny = tokeny[i + rzad]
        przejscia[kontekst][nastepny] += 1

    liczba_przejsc = len(tokeny) - rzad
    h = 0.0
    for _, cnt in przejscia.items():
        suma = sum(cnt.values())
        p_kontekst = suma / liczba_przejsc
        h_lokalne = 0.0
        for _, ile in cnt.items():
            p = ile / suma
            h_lokalne -= p * math.log2(p)
        h += p_kontekst * h_lokalne
    return h


def analiza_jezyka(path, max_rzad=5):
    if not path.is_file():
        print("Brak pliku:", path)
        print()
        return None

    tekst = wczytaj_znaki(path)
    slowa = tokeny_slowa(tekst)

    print("=== Analiza:", path.name, "===")
    print("Liczba znakow:", len(tekst))
    print("Liczba slow:", len(slowa))
    print()

    print("Znaki:")
    print("H(znaki):", f"{entropia_podstawowa(list(tekst)):.6f}", "bit")
    for rzad in range(1, max_rzad + 1):
        h = entropia_warunkowa(list(tekst), rzad)
        print(f"H(znaki | kontekst {rzad}): {h:.6f} bit")
    print()

    print("Slowa:")
    print("H(slowa):", f"{entropia_podstawowa(slowa):.6f}", "bit")
    for rzad in range(1, max_rzad + 1):
        h = entropia_warunkowa(slowa, rzad)
        print(f"H(slowa | kontekst {rzad}): {h:.6f} bit")
    print()

    h1 = entropia_warunkowa(list(tekst), 1)
    h2 = entropia_warunkowa(list(tekst), 2)
    h3 = entropia_warunkowa(list(tekst), 3)
    return {
        "path": path,
        "h_char_1": h1,
        "h_char_2": h2,
        "h_char_3": h3,
    }


def czy_jezyk_naturalny(wynik, prog_h3=2.7):
    # Bardzo prosty heurystyczny test:
    # - entropia warunkowa powinna maleć dla kolejnych rzedow
    # - H3 dla znakow zwykle jest wyraznie nizsze niz dla losowego tekstu
    maleje = (wynik["h_char_1"] >= wynik["h_char_2"] >= wynik["h_char_3"])
    niski_poziom = (wynik["h_char_3"] <= prog_h3)
    return maleje and niski_poziom


max_rzad = 5
if len(sys.argv) > 1:
    max_rzad = int(sys.argv[1])

pliki_referencyjne = [
    Path("norm_wiki_en.txt"),
    Path("norm_wiki_la.txt"),
]

print("Analiza jezykow referencyjnych")
print("==============================")
wyniki_ref = []
for p in pliki_referencyjne:
    wynik = analiza_jezyka(p, max_rzad=max_rzad)
    if wynik is not None:
        wyniki_ref.append(wynik)

print("Analiza plikow sample")
print("=====================")
wyniki_sample = []
for i in range(6):
    p = Path(f"sample{i}.txt")
    wynik = analiza_jezyka(p, max_rzad=max_rzad)
    if wynik is None:
        continue
    wyniki_sample.append(wynik)
    naturalny = czy_jezyk_naturalny(wynik)
    decyzja = "TAK" if naturalny else "NIE"
    print("Wniosek dla", p.name + ":", "czy jezyk naturalny?", decyzja)
    print()

if not wyniki_sample:
    print("Brak plikow sample0..sample5 w katalogu.")
