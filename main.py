import random
from typing import List


def generate_zero_order_text(length: int, rng: random.Random) -> str:
    # if rng is None:
    #     rng = random.Random()
    rng = random.Random()
    return "".join(rng.choice(ALPHABET) for _ in range(length))


def split_words_by_spaces(text) -> List[str]:
    words = []
    current_word = []

    for ch in text:
        if ch == " ":
            if current_word:
                words.append("".join(current_word))
                current_word = []
        else:
            current_word.append(ch)

    return words


def average_word_length(text) -> float:
    words = split_words_by_spaces(text)

    if not words:
        return 0.0

    total_len = 0
    for word in words:
        total_len += len(word)

    average = total_len / len(words)
    return average


ALPHABET = "abcdefghijklmnopqrstuvwxyz "

generated_length = 100000

rng = random.Random(12345)

text = generate_zero_order_text(generated_length,rng)
avg_len = average_word_length(text)

print(f"Długość wygenerowanego tekstu: {len(text)} znaków")
print(f"Liczba słów: {len(split_words_by_spaces(text))}")
print(f"Średnia długość słowa: {avg_len:.4f}")
