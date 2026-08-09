import os
import requests
from dotenv import load_dotenv
from google import genai

# تحميل ملف .env

load_dotenv()

# =========================
# Gemini
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None

if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("GEMINI CLIENT: READY")
    except Exception as e:
        print("GEMINI CLIENT ERROR:", e)
else:
    print("GEMINI_API_KEY: NOT FOUND")

# =========================
# Ollama
# =========================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

print("BRAIN.PY LOADED - GEMINI + OLLAMA READY")

# =========================
# Gemini
# =========================

def ask_gemini(message):
    if gemini_client is None:
        print("Gemini ERROR: client غير جاهز.")
        return None

    try:
        print("Trying Gemini...")

        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=message
        )

        if response and response.text:
            print("Gemini response received.")
            return response.text.strip()

        print("Gemini returned empty response.")
        return None

    except Exception as e:
        print("Gemini ERROR:", e)
        return None


# =========================
# Ollama
# =========================

def ask_ollama(message):
    try:
        print("Trying Ollama...")

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

        answer = data.get("response")

        if answer:
            print("Ollama response received.")
            return answer.strip()

        return None

    except Exception as e:
        print("Ollama ERROR:", e)
        return None


# =========================
# Ido AI
# =========================

def get_response(message):

    original_message = message.strip()
    message_lower = original_message.lower()

    # =========================
    # الردود السريعة والثابتة
    # =========================

    responses = {

        "hello":
            "Hello! أنا Ido AI 🤖",

        "hi":
            "Hello! أنا Ido AI 🤖",

        "مرحبا":
            "مرحبًا بك! كيف يمكنني مساعدتك؟ 😊",

        "سلام":
            "وعليكم السلام! كيف حالك؟ 😊",

        "اسمك":
            "أنا Ido AI 🤖",

        "ما اسمك":
            "أنا Ido AI 🤖",

        "كيف حالك":
            "أنا بخير، شكرًا لسؤالك 😊",

        # =========================
        # هوية Ido AI
        # =========================

        "من صنعك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        "من طورك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        "من بناك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        "من هو مطورك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        "من برمجك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        "من اخترعك":
            "تم تطويري وبنائي بواسطة نوفل الأهدي، وأدعى Ido AI 🤖",

        # =========================
        # معلومات عامة
        # =========================

        "الوقت":
            "يمكنك معرفة الوقت من النظام ⏰",

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم حوالي 8 مليارات نسمة 🌍",

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو تقنية تجعل الحاسوب قادرًا على فهم الأوامر والتعلم واتخاذ القرارات 🤖",

        "ما هي بايثون":
            "Python هي لغة برمجة قوية وسهلة تستخدم في تطوير البرامج والذكاء الاصطناعي 🐍",

        "ما هي عاصمة المغرب":
            "عاصمة المغرب هي الرباط 🇲🇦",

        "ما هي عاصمة فرنسا":
            "عاصمة فرنسا هي باريس 🇫🇷",

        # =========================
        # المجاملات
        # =========================

        "شكرا":
            "على الرحب والسعة 😊",

        "شكراً":
            "العفو 😊",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا 😊",
    }

    # =========================
    # البحث في الردود الجاهزة
    # =========================

    for key, value in responses.items():

        if key in message_lower:
            return value

    # =========================
    # Gemini أولًا
    # =========================

    answer = ask_gemini(original_message)

    if answer:
        return answer

    # =========================
    # Ollama ثانيًا
    # =========================

    print("Gemini failed. Trying Ollama...")

    answer = ask_ollama(original_message)

    if answer:
        return answer

    # =========================
    # فشل الاثنين
    # =========================

    return "أنا Ido AI 🤖 لم أجد إجابة حاليًا."