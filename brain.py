import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

# تحميل ملف .env
load_dotenv()

# =========================
# Gemini
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None

if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )
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
# Gemini - نص
# =========================

def ask_gemini(message):

    if gemini_client is None:
        print("Gemini ERROR: client غير جاهز.")
        return None

    try:
        print("Trying Gemini...")

        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash",
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
# Gemini - صورة
# =========================

def ask_gemini_image(message, image_bytes, mime_type):

    if gemini_client is None:
        print("Gemini ERROR: client غير جاهز.")
        return None

    try:
        print("Trying Gemini with image...")

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                message,
                image_part
            ]
        )

        if response and response.text:
            print("Gemini image response received.")
            return response.text.strip()

        print("Gemini returned empty image response.")
        return None

    except Exception as e:
        print("Gemini IMAGE ERROR:", e)
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

        print("Ollama returned empty response.")
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
            "السلام عليكم ورحمة الله وبركاته. أنا Ido AI، كيف يمكنني مساعدتك؟",

        "hi":
            "السلام عليكم ورحمة الله وبركاته. أنا Ido AI، كيف يمكنني مساعدتك؟",

        "مرحبا":
            "السلام عليكم ورحمة الله وبركاته. مرحبًا بك، كيف يمكنني مساعدتك؟",

        "سلام":
            "وعليكم السلام ورحمة الله وبركاته. كيف يمكنني مساعدتك؟",

        "اسمك":
            "أنا Ido AI.",

        "ما اسمك":
            "أنا Ido AI.",

        "كيف حالك":
            "أنا بخير، شكرًا لسؤالك. كيف يمكنني مساعدتك؟",

        # =========================
        # هوية Ido AI
        # =========================

        "من صنعك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من طورك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من بناك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من هو مطورك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من برمجك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من اخترعك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من انشاك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من أنشأك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من صممك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من صاحبك":
            "أنا Ido AI، وقد تم تطويري وبنائي بواسطة Noufal Ouhadi.",

        "من وراءك":
            "تم تطويري وبنائي بواسطة Noufal Ouhadi، وأنا Ido AI.",

        "من صنع ido ai":
            "تم تطوير Ido AI وبناؤه بواسطة Noufal Ouhadi.",

        "من طور ido ai":
            "تم تطوير Ido AI بواسطة Noufal Ouhadi.",

        # =========================
        # معلومات عامة
        # =========================

        "الوقت":
            "يمكنك معرفة الوقت من النظام.",

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم أكثر من 8 مليارات نسمة.",

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو مجال من علوم الحاسوب يهدف إلى تطوير أنظمة قادرة على فهم المعلومات والتعلم منها وتنفيذ مهام تحتاج عادةً إلى قدر من الذكاء البشري.",

        "ما هي بايثون":
            "Python هي لغة برمجة قوية وسهلة الاستخدام، وتُستخدم في تطوير البرامج والذكاء الاصطناعي وتحليل البيانات.",

        "ما هي عاصمة المغرب":
            "عاصمة المغرب هي الرباط.",

        "ما هي عاصمة فرنسا":
            "عاصمة فرنسا هي باريس.",

        # =========================
        # المجاملات
        # =========================

        "شكرا":
            "على الرحب والسعة.",

        "شكراً":
            "العفو، يسعدني مساعدتك.",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا."
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

    return "أنا Ido AI ولم أجد إجابة حاليًا."


# =========================
# تحليل صورة
# =========================

def get_image_response(
    message,
    image_bytes,
    mime_type
):

    if not message or not message.strip():
        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    # Gemini مع الصورة
    answer = ask_gemini_image(
        message.strip(),
        image_bytes,
        mime_type
    )

    if answer:
        return answer

    return "تعذر تحليل الصورة حاليًا."