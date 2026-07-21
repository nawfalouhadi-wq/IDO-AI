import requests
import os


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
        return data.get("response", None)

    except Exception:
        return None


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

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم حوالي 8 مليارات نسمة 🌍",

    }


    # البحث عن رد جاهز
    for key, answer in responses.items():
        if key in message:
            return answer


    # تجربة Ollama
    ollama_answer = ask_ollama(message)

    if ollama_answer:
        return ollama_answer


    # إذا لم يعمل Ollama
    return "أنا Ido AI 🤖 لا أملك إجابة لهذا السؤال حاليًا، لكن يمكنك تشغيل Ollama للحصول على ذكاء اصطناعي أقوى."

