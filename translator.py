translations = {
    "hello": "bonjour",
    "hi": "salut",
    "dog": "chien",
    "cat": "chat",
    "book": "livre",
    "computer": "ordinateur",
    "phone": "téléphone",
    "water": "eau",
    "food": "nourriture"
}

reverse_translations = {v: k for k, v in translations.items()}


def translate(text):
    words = text.lower().split()
    result = []

    for word in words:
        if word in translations:
            result.append(translations[word])
        elif word in reverse_translations:
            result.append(reverse_translations[word])
        else:
            result.append(word)

    return " ".join(result)