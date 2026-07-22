import os
import requests

from dotenv import load_dotenv
from openai import OpenAI

# تحميل متغيرات البيئة
load_dotenv()

# رابط Ollama
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

# مفتاح OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# إنشاء العميل فقط إذا كان المفتاح موجودًا
client = None

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

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
            timeout=60
        )

        print("Ollama Status:", response.status_code)

        if response.status_code != 200:
            print("Ollama Response:", response.text)
            return None

        data = response.json()

        return data.get("response")

    except Exception as e:
        print("Ollama ERROR:", e)
        return None


# -------------------------
# OpenAI
# -------------------------

def ask_openai(message):

    if client is None:
        print("OpenAI ERROR: OPENAI_API_KEY غير موجود.")
        return None

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
        print("OpenAI ERROR:", e)
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

        "كيف حالك": "أنا بخير، شكراً لسؤالك 😊",

        "من صنعك": "أنا مشروع ذكاء اصطناعي اسمه Ido AI 🤖",

        "الوقت": "يمكنك معرفة الوقت من النظام ⏰",

        "كم عدد الناس في العالم": "يبلغ عدد سكان العالم حوالي 8 مليارات نسمة 🌍",

        "ما هو الذكاء الاصطناعي": "الذكاء الاصطناعي هو تقنية تجعل الحاسوب قادرًا على التعلم وفهم الأوامر واتخاذ القرارات 🤖",

        "ما هي بايثون": "Python هي لغة برمجة قوية وسهلة تستخدم في تطوير البرامج والذكاء الاصطناعي 🐍",

        "ما هي عاصمة المغرب": "عاصمة المغرب هي الرباط 🇲🇦",

        "ما هي عاصمة فرنسا": "عاصمة فرنسا هي باريس 🇫🇷",

        "شكرا": "على الرحب والسعة 😊",

        "شكراً": "العفو 😊",

        "وداعا": "إلى اللقاء! أتمنى لك يوماً سعيداً 😊",
    }

    # الردود الجاهزة
    for key, value in responses.items():
        if key in message:
            return value

    # تجربة Ollama
    answer = ask_ollama(message)

    if answer:
        return answer

    # تجربة OpenAI
    answer = ask_openai(message)

    if answer:
        return answer

    # إذا لم يعمل أي شيء
    return "أنا Ido AI 🤖 لم أجد إجابة حالياً."