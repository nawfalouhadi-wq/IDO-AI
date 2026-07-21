import requests
import os


# رابط Ollama
# إذا وضعت رابط خارجي في المتغير OLLAMA_URL سيستخدمه
# وإذا لم يوجد سيستخدم Ollama الموجود في الجهاز
OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434"
)


def ask_ollama(message):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
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

    return ask_ollama(message)