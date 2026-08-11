import os
import base64
import requests

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import HttpOptions


# =========================================================
# تحميل ملف .env
# =========================================================

load_dotenv()


# =========================================================
# إعدادات عامة
# =========================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "10")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "120"))
)


# =========================================================
# Gemini
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

gemini_client = None

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=5000
            )
        )

        print(
            "GEMINI CLIENT: READY"
        )

    except Exception as e:

        print(
            "GEMINI CLIENT ERROR:",
            e
        )

        gemini_client = None

else:

    print(
        "GEMINI_API_KEY: NOT FOUND"
    )


# =========================================================
# OpenRouter
# =========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
    )

else:

    print(
        "OPENROUTER_API_KEY: NOT FOUND"
    )


# =========================================================
# معلومات التشغيل
# =========================================================

print(
    "BRAIN.PY LOADED - "
    "GEMINI + OPENROUTER READY"
)


# =========================================================
# أداة تنظيف النص
# =========================================================

def clean_answer(answer):

    if answer is None:

        return None

    try:

        answer = str(answer).strip()

        if not answer:

            return None

        return answer

    except Exception:

        return None


# =========================================================
# Gemini - نص
# =========================================================

def ask_gemini(message):

    if gemini_client is None:

        print(
            "Gemini ERROR: "
            "client غير جاهز."
        )

        return None

    if not message:

        return None

    try:

        print(
            "Trying Gemini..."
        )

        # =================================================
        # Gemini 3.6 Flash
        # =================================================

        response = (
            gemini_client.models.generate_content(

                model="gemini-3.6-flash",

                contents=message
            )
        )

        if response:

            answer = clean_answer(
                response.text
            )

            if answer:

                print(
                    "Gemini response received."
                )

                return answer

        print(
            "Gemini returned empty response."
        )

        return None

    except Exception as e:

        print(
            "Gemini ERROR:",
            e
        )

        return None


# =========================================================
# OpenRouter - نص
# =========================================================

def ask_openrouter(message):

    if not OPENROUTER_API_KEY:

        print(
            "OpenRouter ERROR: "
            "API key غير موجود."
        )

        return None

    if not message:

        return None

    try:

        print(
            "Trying OpenRouter..."
        )

        response = requests.post(

            OPENROUTER_URL,

            headers={

                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "X-Title":
                    "Aido AI"
            },

            json={

                "model":
                    "openrouter/free",

                "messages": [

                    {

                        "role":
                            "user",

                        "content":
                            message
                    }
                ]
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter Response:",
                response.text[:2000]
            )

            return None

        try:

            data = response.json()

        except Exception as e:

            print(
                "OpenRouter JSON ERROR:",
                e
            )

            return None

        choices = data.get(
            "choices",
            []
        )

        if choices:

            message_data = choices[0].get(
                "message",
                {}
            )

            answer = clean_answer(
                message_data.get(
                    "content"
                )
            )

            if answer:

                print(
                    "OpenRouter response received."
                )

                return answer

        print(
            "OpenRouter returned empty response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "OpenRouter ERROR: request timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "OpenRouter ERROR: connection failed."
        )

        return None

    except Exception as e:

        print(
            "OpenRouter ERROR:",
            e
        )

        return None


# =========================================================
# Gemini - صورة
# =========================================================

def ask_gemini_image(
    message,
    image_bytes,
    mime_type
):

    if gemini_client is None:

        print(
            "Gemini ERROR: "
            "client غير جاهز."
        )

        return None

    if not image_bytes:

        print(
            "Gemini IMAGE ERROR: "
            "الصورة فارغة."
        )

        return None

    try:

        print(
            "Trying Gemini with image..."
        )

        image_part = types.Part.from_bytes(

            data=image_bytes,

            mime_type=mime_type
        )

        response = (
            gemini_client.models.generate_content(

                # =================================================
                # Gemini 3.6 Flash
                # =================================================

                model="gemini-3.6-flash",

                contents=[

                    message,

                    image_part
                ]
            )
        )

        if response:

            answer = clean_answer(
                response.text
            )

            if answer:

                print(
                    "Gemini image response received."
                )

                return answer

        print(
            "Gemini returned empty "
            "image response."
        )

        return None

    except Exception as e:

        print(
            "Gemini IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# OpenRouter - صورة
# =========================================================

def ask_openrouter_image(
    message,
    image_bytes,
    mime_type
):

    if not OPENROUTER_API_KEY:

        print(
            "OpenRouter ERROR: "
            "API key غير موجود."
        )

        return None

    if not image_bytes:

        print(
            "OpenRouter IMAGE ERROR: "
            "الصورة فارغة."
        )

        return None

    try:

        print(
            "Trying OpenRouter with image..."
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        response = requests.post(

            OPENROUTER_URL,

            headers={

                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "X-Title":
                    "Aido AI"
            },

            json={

                "model":
                    "openrouter/free",

                "messages": [

                    {

                        "role":
                            "user",

                        "content": [

                            {

                                "type":
                                    "text",

                                "text":
                                    message
                            },

                            {

                                "type":
                                    "image_url",

                                "image_url": {

                                    "url":
                                        image_data_url
                                }
                            }
                        ]
                    }
                ]
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter Image Response:",
                response.text[:2000]
            )

            return None

        try:

            data = response.json()

        except Exception as e:

            print(
                "OpenRouter Image JSON ERROR:",
                e
            )

            return None

        choices = data.get(
            "choices",
            []
        )

        if choices:

            message_data = choices[0].get(
                "message",
                {}
            )

            answer = clean_answer(
                message_data.get(
                    "content"
                )
            )

            if answer:

                print(
                    "OpenRouter image response "
                    "received."
                )

                return answer

        print(
            "OpenRouter returned empty "
            "image response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "OpenRouter IMAGE ERROR: "
            "request timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "OpenRouter IMAGE ERROR: "
            "connection failed."
        )

        return None

    except Exception as e:

        print(
            "OpenRouter IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Ido AI
# =========================================================

def get_response(message):

    if not message:

        return "اكتب رسالة أولًا."

    original_message = str(
        message
    ).strip()

    if not original_message:

        return "اكتب رسالة أولًا."

    message_lower = (
        original_message.lower()
    )


    # =====================================================
    # الردود السريعة والثابتة
    # =====================================================

    responses = {

        "hello":
            "السلام عليكم ورحمة الله وبركاته. "
            "أنا Ido AI، كيف يمكنني مساعدتك؟",

        "hi":
            "السلام عليكم ورحمة الله وبركاته. "
            "أنا Ido AI، كيف يمكنني مساعدتك؟",

        "مرحبا":
            "السلام عليكم ورحمة الله وبركاته. "
            "مرحبًا بك، كيف يمكنني مساعدتك؟",

        "سلام":
            "وعليكم السلام ورحمة الله وبركاته. "
            "كيف يمكنني مساعدتك؟",

        "اسمك":
            "أنا Ido AI.",

        "ما اسمك":
            "أنا Ido AI.",

        "كيف حالك":
            "أنا بخير، شكرًا لسؤالك. "
            "كيف يمكنني مساعدتك؟",

        "من صنعك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من طورك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من بناك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من هو مطورك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من برمجك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من اخترعك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من انشاك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من أنشأك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صممك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صاحبك":
            "أنا Ido AI، وقد تم تطويري "
            "وبنائي بواسطة Noufal Ouhadi.",

        "من وراءك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صنع ido ai":
            "تم تطوير Ido AI وبناؤه "
            "بواسطة Noufal Ouhadi.",

        "من طور ido ai":
            "تم تطوير Ido AI بواسطة "
            "Noufal Ouhadi.",

        "الوقت":
            "يمكنك معرفة الوقت من النظام.",

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم "
            "أكثر من 8 مليارات نسمة.",

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو مجال من علوم "
            "الحاسوب يهدف إلى تطوير أنظمة قادرة "
            "على فهم المعلومات والتعلم منها "
            "وتنفيذ مهام تحتاج عادةً إلى قدر "
            "من الذكاء البشري.",

        "ما هي بايثون":
            "Python هي لغة برمجة قوية وسهلة "
            "الاستخدام، وتُستخدم في تطوير "
            "البرامج والذكاء الاصطناعي "
            "وتحليل البيانات.",

        "ما هي عاصمة المغرب":
            "عاصمة المغرب هي الرباط.",

        "ما هي عاصمة فرنسا":
            "عاصمة فرنسا هي باريس.",

        "شكرا":
            "على الرحب والسعة.",

        "شكراً":
            "العفو، يسعدني مساعدتك.",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا."
    }


    # =====================================================
    # البحث في الردود الجاهزة
    # =====================================================

    for key, value in responses.items():

        if key in message_lower:

            return value


    # =====================================================
    # Gemini أولًا
    # =====================================================

    answer = ask_gemini(
        original_message
    )

    if answer:

        return answer


    # =====================================================
    # OpenRouter ثانيًا
    # =====================================================

    print(
        "Gemini failed. "
        "Trying OpenRouter..."
    )

    answer = ask_openrouter(
        original_message
    )

    if answer:

        return answer


    # =====================================================
    # فشل Gemini و OpenRouter
    # =====================================================

    return (
        "أنا Ido AI ولم أجد إجابة حاليًا."
    )


# =========================================================
# تحليل صورة
# =========================================================

def get_image_response(
    message,
    image_bytes,
    mime_type
):

    if not image_bytes:

        return (
            "لم يتم إرسال صورة صالحة."
        )

    if not mime_type:

        mime_type = "image/jpeg"

    if not mime_type.startswith("image/"):

        return (
            "الملف المرسل ليس صورة صالحة."
        )

    if not message or not message.strip():

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    message = message.strip()


    # =====================================================
    # Gemini مع الصورة أولًا
    # =====================================================

    answer = ask_gemini_image(

        message,

        image_bytes,

        mime_type
    )

    if answer:

        return answer


    # =====================================================
    # إذا فشل Gemini في الصورة
    # الانتقال إلى OpenRouter
    # =====================================================

    print(
        "Gemini image failed. "
        "Trying OpenRouter image..."
    )

    answer = ask_openrouter_image(

        message,

        image_bytes,

        mime_type
    )

    if answer:

        return answer


    # =====================================================
    # فشل Gemini و OpenRouter
    # =====================================================

    return (
        "تعذر تحليل الصورة حاليًا."
    )