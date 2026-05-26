from collections import Counter
from pathlib import Path
import sys

# Kod Morse dla liter a-z (kropki i kreski)
MORSE_PATTERN = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
}

path = Path("../norm_romeo.txt")
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

if not path.is_file():
    print("Brak pliku:", path)
    sys.exit(1)

text = path.read_text(encoding="utf-8")
counter = Counter(text)
total = sum(counter.values())


rel = {}
for ch, cnt in counter.items():
    rel[ch] = cnt / total


ordered = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

print("Plik:", path)
print("Znaki w analizie:", total)
print()
print("Znak | Liczba | prawdopodobienstwo")
print("-----+--------+------------------")
for ch, n in ordered:
    p = rel[ch]
    if ch == " ":
        display = " '" + " " + "'"
    else:
        display = " '" + ch + "'"
    print(display.rjust(4), "|", str(n).rjust(6), "|", f"{p:.6f}")

print()
print("Litery A-Z - czestosc vs dlugosc kodu Morse:")
print("Litera |  P(lit) | Morse (symb.)")
print("-------+---------+---------------")
for c in sorted(MORSE_PATTERN):
    p = rel.get(c, 0.0)
    mlen = len(MORSE_PATTERN[c])
    print(" ", "'" + c + "'", " |", f"{p:.6f}", "|", mlen)

print()
print(
    "Czestsze litery maja zwykle krotszy kod Morse (np. e, t), "
    "rzadsze dluzszy - tak skraca sie sredni czas nadawania."
)
