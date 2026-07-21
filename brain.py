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
                "model": "llama3.1:8b",
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

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو تقنية تجعل الحاسوب قادرًا على التعلم وفهم الأوامر واتخاذ قرارات 🤖",

        "ما هي بايثون":
            "Python هي لغة برمجة سهلة وقوية تستخدم في تطوير البرامج والذكاء الاصطناعي 🐍",

        "ما هي عاصمة المغرب":
            "عاصمة المغرب هي الرباط 🇲🇦",

        "ما هي عاصمة فرنسا":
            "عاصمة فرنسا هي باريس 🇫🇷",

        "من هو رئيس المغرب":
            "رئيس الدولة في المغرب هو الملك محمد السادس 🇲🇦",

        "شكرا":
            "على الرحب والسعة! 😊",

        "شكراً":
            "العفو! أنا هنا لمساعدتك 🤖",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا 😊",

    }


    for key, answer in responses.items():
        if key in message:
            return answer


    ollama_answer = ask_ollama(message)

    if ollama_answer:
        return ollama_answer


    return "أنا Ido AI 🤖 لم أجد إجابة لهذا السؤال حاليًا."

