import requests


def ask_ollama(message):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": message,
                "stream": False
            },
            timeout=120
        )

        data = response.json()
        return data["response"]

    except Exception as e:
        return f"خطأ في الاتصال بـ Ollama: {e}"


def get_response(message):
    message = message.lower().strip()

    responses = {

        "hello": "Hello! أنا Ido AI 🤖",
        "hi": "Hello! أنا Ido AI 🤖",

        "مرحبا": "مرحبًا بك! كيف يمكنني مساعدتك؟ 😊",
        "سلام": "وعليكم السلام! كيف حالك؟ 😊",

        "اسمك": "أنا Ido AI 🤖",

        "كيف حالك": "أنا بخير، شكرًا لسؤالك 😊",

        "من صنعك": "أنا مشروع ذكاء اصطناعي اسمه Ido AI 🤖",

        "الوقت": "يمكنك معرفة الوقت من النظام ⏰",

    }

    for key, answer in responses.items():
        if key in message:
            return answer

    # إذا لم يجد جوابًا محفوظًا، يسأل Ollama
    return ask_ollama(message)