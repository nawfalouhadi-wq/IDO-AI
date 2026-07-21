import requests
import os

from dotenv import load_dotenv
from openai import OpenAI


# تحميل ملف .env
load_dotenv()


# رابط Ollama
OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434"
)


# OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


print("BRAIN.PY LOADED - OLLAMA + OPENAI READY")


# -------------------------
# Ollama
# -------------------------

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

        print("Ollama status:", response.status_code)

        data = response.json()

        return data.get("response")

    except Exception as e:
        print("Ollama error:", e)
        return None



# -------------------------
# OpenAI
# -------------------------

def ask_openai(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI error:", e)
        return None



# -------------------------
# Ido AI
# -------------------------

def get_response(message):

    message = message.lower().strip()


    responses = {

        "hello": "Hello! أنا Ido AI 🤖",
        "hi": "Hello! أنا Ido AI 🤖",

        "مرحبا": "مرحبًا بك! كيف يمكنني مساعدتك؟ 😊",
        "سلام": "وعليكم السلام! كيف حالك؟ 😊",

        "اسمك": "أنا Ido AI 🤖",

        "كيف حالك":
            "أنا بخير، شكرًا لسؤالك 😊",

        "من صنعك":
            "أنا مشروع ذكاء اصطناعي اسمه Ido AI 🤖",

        "الوقت":
            "يمكنك معرفة الوقت من النظام ⏰",

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم حوالي 8 مليارات نسمة 🌍",

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو تقنية تجعل الحاسوب قادرًا على التعلم وفهم الأوامر واتخاذ القرارات 🤖",

        "ما هي بايثون":
            "Python هي لغة برمجة قوية وسهلة تستخدم في تطوير البرامج والذكاء الاصطناعي 🐍",

        "ما هي عاصمة المغرب":
            "عاصمة المغرب هي الرباط 🇲🇦",

        "ما هي عاصمة فرنسا":
            "عاصمة فرنسا هي باريس 🇫🇷",

        "شكرا":
            "على الرحب والسعة! 😊",

        "شكراً":
            "العفو! أنا هنا لمساعدتك 🤖",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا 😊",

    }


    # الردود الجاهزة
    for key, answer in responses.items():
        if key in message:
            return answer



    # 1) تجربة Ollama
    ollama_answer = ask_ollama(message)

    if ollama_answer:
        return ollama_answer



    # 2) إذا لم يعمل Ollama استخدم OpenAI
    openai_answer = ask_openai(message)

    if openai_answer:
        return openai_answer



    # 3) إذا فشل كل شيء
    return "أنا Ido AI 🤖 لم أجد إجابة حاليًا."