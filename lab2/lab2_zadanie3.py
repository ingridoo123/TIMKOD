import random
import sys
from collections import Counter, defaultdict
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

if len(slowa) < 3:
    print("Za malo slow do modelu Markowa.")
    sys.exit(1)

licznik_slow = Counter(slowa)
slownik = list(licznik_slow.keys())
wagi = list(licznik_slow.values())

przejscia_1 = defaultdict(Counter)
for i in range(len(slowa) - 1):
    a = slowa[i]
    b = slowa[i + 1]
    przejscia_1[a][b] += 1

przejscia_2 = defaultdict(Counter)
for i in range(len(slowa) - 2):
    a = slowa[i]
    b = slowa[i + 1]
    c = slowa[i + 2]
    przejscia_2[(a, b)][c] += 1


def losuj_z_counter(cnt, rng):
    if not cnt:
        return rng.choices(slownik, weights=wagi, k=1)[0]
    lokalne_slowa = list(cnt.keys())
    lokalne_wagi = list(cnt.values())
    return rng.choices(lokalne_slowa, weights=lokalne_wagi, k=1)[0]


def generuj_markov_1(ile, rng):
    wynik = [rng.choices(slownik, weights=wagi, k=1)[0]]
    while len(wynik) < ile:
        ostatnie = wynik[-1]
        nastepne = losuj_z_counter(przejscia_1[ostatnie], rng)
        wynik.append(nastepne)
    return wynik


def generuj_markov_2(ile, rng):
    wynik = [slowa[0], slowa[1]]
    while len(wynik) < ile:
        para = (wynik[-2], wynik[-1])
        if para in przejscia_2:
            nastepne = losuj_z_counter(przejscia_2[para], rng)
        else:
            nastepne = losuj_z_counter(przejscia_1[wynik[-1]], rng)
        wynik.append(nastepne)
    return wynik[:ile]


def generuj_markov_2_od_slowa(ile, start_slowo, rng):
    wynik = [start_slowo]
    drugie = losuj_z_counter(przejscia_1[start_slowo], rng)
    wynik.append(drugie)

    while len(wynik) < ile:
        para = (wynik[-2], wynik[-1])
        if para in przejscia_2:
            nastepne = losuj_z_counter(przejscia_2[para], rng)
        else:
            nastepne = losuj_z_counter(przejscia_1[wynik[-1]], rng)
        wynik.append(nastepne)
    return wynik[:ile]


ziarno = 3333
rng1 = random.Random(ziarno)
rng2 = random.Random(ziarno)
rng2_start = random.Random(ziarno)

tekst_markov_1 = generuj_markov_1(ile_slow_generowac, rng1)
tekst_markov_2 = generuj_markov_2(ile_slow_generowac, rng2)
tekst_markov_2_probability = generuj_markov_2_od_slowa(
    ile_slow_generowac,
    start_slowo="probability",
    rng=rng2_start,
)

print("Plik:", path)
print("Liczba slow w korpusie:", len(slowa))
print("Liczba wygenerowanych slow:", ile_slow_generowac)
print("Ziarno RNG:", ziarno)
print()
print("Markov 1. rzedu (na slowach):")
print(" ".join(tekst_markov_1))
print()
print("Markov 2. rzedu (na slowach):")
print(" ".join(tekst_markov_2))
print()
print("Markov 2. rzedu (start od 'probability'):")
print(" ".join(tekst_markov_2_probability))
