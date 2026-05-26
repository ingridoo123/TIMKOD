import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

path = Path("../norm_wiki_sample.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

tekst = path.read_text(encoding="utf-8")

licznik = Counter(tekst)
znaki = list(licznik.keys())
wagi = list(licznik.values())

after1 = defaultdict(Counter)
for i in range(len(tekst) - 1):
    a = tekst[i]
    b = tekst[i + 1]
    after1[a][b] += 1

after3 = defaultdict(Counter)
for i in range(len(tekst) - 3):
    kontekst = tekst[i:i + 3]
    nastepny = tekst[i + 3]
    after3[kontekst][nastepny] += 1

after5 = defaultdict(Counter)
for i in range(len(tekst) - 5):
    kontekst = tekst[i:i + 5]
    nastepny = tekst[i + 5]
    after5[kontekst][nastepny] += 1


def srednia_dlugosc_slowa(t):
    words = []
    current_word = []
    for ch in t:
        if ch == " ":
            if current_word:
                words.append("".join(current_word))
                current_word = []
        else:
            current_word.append(ch)
    if not words:
        return 0.0
    suma = 0
    for w in words:
        suma += len(w)
    return suma / len(words)


def losuj_z_counter(cnt, rng):
    if not cnt:
        return rng.choices(znaki, weights=wagi, k=1)[0]
    litery = list(cnt.keys())
    local_wagi = list(cnt.values())
    return rng.choices(litery, weights=local_wagi, k=1)[0]


def generuj_rzad_1(dlugosc, rng):
    wynik = [rng.choices(znaki, weights=wagi, k=1)[0]]
    while len(wynik) < dlugosc:
        ostatni = wynik[-1]
        nowy = losuj_z_counter(after1[ostatni], rng)
        wynik.append(nowy)
    return "".join(wynik)


def generuj_rzad_3(dlugosc, rng):
    start = tekst[:3]
    wynik = list(start)
    while len(wynik) < dlugosc:
        k3 = "".join(wynik[-3:])
        if k3 in after3:
            nowy = losuj_z_counter(after3[k3], rng)
        else:
            nowy = losuj_z_counter(after1[wynik[-1]], rng)
        wynik.append(nowy)
    return "".join(wynik[:dlugosc])


def generuj_rzad_5(dlugosc, rng, start="probability"):
    wynik = list(start)
    while len(wynik) < dlugosc:
        k5 = "".join(wynik[-5:])
        if k5 in after5:
            nowy = losuj_z_counter(after5[k5], rng)
        else:
            k3 = "".join(wynik[-3:])
            if k3 in after3:
                nowy = losuj_z_counter(after3[k3], rng)
            else:
                nowy = losuj_z_counter(after1[wynik[-1]], rng)
        wynik.append(nowy)
    return "".join(wynik[:dlugosc])


dlugosc_wyjscia = 100000
ziarno = 3333
rng1 = random.Random(ziarno)
rng3 = random.Random(ziarno)
rng5 = random.Random(ziarno)

tekst_rzad_1 = generuj_rzad_1(dlugosc_wyjscia, rng1)
tekst_rzad_3 = generuj_rzad_3(dlugosc_wyjscia, rng3)
tekst_rzad_5 = generuj_rzad_5(dlugosc_wyjscia, rng5, start="probability")

srednia_korpus = srednia_dlugosc_slowa(tekst)
srednia_1 = srednia_dlugosc_slowa(tekst_rzad_1)
srednia_3 = srednia_dlugosc_slowa(tekst_rzad_3)
srednia_5 = srednia_dlugosc_slowa(tekst_rzad_5)

print("Plik:", path)
print("Dlugosc korpusu:", len(tekst))
print("Dlugosc generowanych tekstow:", dlugosc_wyjscia)
print("Ziarno RNG:", ziarno)
print()
print("Srednia dlugosc slowa w korpusie: ", f"{srednia_korpus:.4f}")
print("Srednia dlugosc slowa Markov rzad 1:", f"{srednia_1:.4f}")
print("Srednia dlugosc slowa Markov rzad 3:", f"{srednia_3:.4f}")
print("Srednia dlugosc slowa Markov rzad 5:", f"{srednia_5:.4f}")
print()
print("Start dla rzedu 5:", repr("probability"))
print()
print("Przyklad (pierwsze 300 znakow):")
print("Rzad 1:", repr(tekst_rzad_1[:300]))
print("Rzad 3:", repr(tekst_rzad_3[:300]))
print("Rzad 5:", repr(tekst_rzad_5[:300]))
