import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def learn(question, answer):
    memory = load_memory()
    memory[question.lower()] = answer
    save_memory(memory)


def get_answer(question):
    memory = load_memory()
    return memory.get(question.lower())