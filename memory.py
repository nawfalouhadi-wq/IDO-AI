import json
import os


MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def learn(question, answer):
    memory = load_memory()

    if "questions" not in memory:
        memory["questions"] = {}

    memory["questions"][question.lower()] = answer

    save_memory(memory)


def get_answer(question):
    memory = load_memory()

    questions = memory.get("questions", {})

    return questions.get(question.lower())


# =========================
# اسم المستخدم
# =========================

def save_user_name(name):
    memory = load_memory()

    memory["user_name"] = name

    save_memory(memory)


def get_user_name():
    memory = load_memory()

    return memory.get("user_name")


# =========================
# حفظ المحادثات
# =========================

def save_conversation(title, messages):
    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []

    conversation = {
        "title": title,
        "messages": messages
    }

    memory["conversations"].append(conversation)

    save_memory(memory)


def get_conversations():
    memory = load_memory()

    return memory.get("conversations", [])


# =========================
# آخر محادثة
# =========================

def get_last_conversation():
    conversations = get_conversations()

    if conversations:
        return conversations[-1]

    return None