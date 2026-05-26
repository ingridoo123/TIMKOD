myTuple = ("John", "Peter", "Vicky")

sentence = "jebac cwela mamona gownojada żulaaa"
words = []
current_word = []

for ch in sentence:
    if ch == " ":
        if current_word:
            words.append("".join(current_word))
            current_word = []
    else:
        current_word.append(ch)

if current_word:
    words.append("".join(current_word))

print(words)

word1 = "elo"
word2 = "gowno"

words.append("".join(word1))
words.append("".join(word2))
#print(words)
