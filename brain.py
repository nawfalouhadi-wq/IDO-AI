# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# PRIMARY TEXT AI:
#     GROQ
#
# TEXT FALLBACK:
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     MISTRAL
#       ↓
#     GEMINI
#       ↓
#     XAI
#       ↓
#     POLLINATIONS
#
# IMAGE ANALYSIS:
#     GROQ VISION
#
# IMAGE GENERATION / EDITING:
#     GEMINI IMAGE
#
# ============================================================

import os
import re
import base64
import mimetypes
from io import BytesIO

import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)


# ============================================================
# API KEYS
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")


# ============================================================
# MODELS
# ============================================================

# -------------------------
# GROQ TEXT
# -------------------------

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
)


# -------------------------
# GROQ VISION
# -------------------------

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


# -------------------------
# OPENROUTER
# -------------------------

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-oss-20b"
)


# -------------------------
# MISTRAL
# -------------------------

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-large-latest"
)


# -------------------------
# GEMINI TEXT
# -------------------------

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-2.5-flash"
)


# -------------------------
# GEMINI IMAGE
# -------------------------

# نموذج Gemini الحديث المخصص للصور.
GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)


# -------------------------
# XAI
# -------------------------

XAI_MODEL = os.getenv(
    "XAI_MODEL",
    "grok-3-mini"
)


# ============================================================
# URLs
# ============================================================

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
)

XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


# ============================================================
# CLIENT STATUS
# ============================================================

print()

if GROQ_API_KEY:
    print("GROQ CLIENT: READY")
else:
    print("GROQ CLIENT: NOT CONFIGURED")


if OPENROUTER_API_KEY:
    print("OPENROUTER CLIENT: READY")
else:
    print("OPENROUTER CLIENT: NOT CONFIGURED")


if MISTRAL_API_KEY:
    print("MISTRAL CLIENT: READY")
else:
    print("MISTRAL CLIENT: NOT CONFIGURED")


if GEMINI_API_KEY:
    print("GEMINI CLIENT: READY")
else:
    print("GEMINI CLIENT: NOT CONFIGURED")


if XAI_API_KEY:
    print("XAI CLIENT: READY")
else:
    print("XAI CLIENT: NOT CONFIGURED")


print()
print("GROQ TEXT MODEL:", GROQ_TEXT_MODEL)
print("GROQ VISION MODEL:", GROQ_VISION_MODEL)
print("GEMINI IMAGE MODEL:", GEMINI_IMAGE_MODEL)

print("=" * 70)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
أنت Ido AI، مساعد ذكاء اصطناعي عربي ذكي.

اسم المطور:
نوفل أوهادي

القواعد المهمة:

1. أجب مباشرة على سؤال المستخدم.
2. لا تخبر المستخدم أن تستخدم نموذجًا آخر.
3. لا تقل إنك لا تستطيع إنشاء الصور إذا كان الطلب
   طلب إنشاء أو تعديل صورة.
4. إذا كان المستخدم يطلب صورة، يجب أن يتعامل
   النظام معها كطلب صورة وليس كسؤال نصي عادي.
5. لا تحول طلب إنشاء الصورة إلى مقال يشرح للمستخدم
   كيف يستخدم Midjourney أو DALL-E أو Stable Diffusion.
6. لا تكتب Image Prompt للمستخدم بدل إنشاء الصورة.
7. عند التحية:
   إذا قال المستخدم "السلام عليكم" فأجب طبيعيًا:
   "وعليكم السلام ورحمة الله وبركاته!"
8. إذا جمع المستخدم التحية مع طلب، لا تكتفِ بالتحية.
   أجب عن الطلب نفسه أيضًا.
9. تحدث بالعربية عندما يكون المستخدم عربيًا.
10. لا تستخدم إجابات محفوظة من الذاكرة للتحيات العامة.
11. كن مختصرًا وواضحًا عندما يكون السؤال بسيطًا.
"""


# ============================================================
# HELPER
# ============================================================

def clean_text(text):
    """
    تنظيف بسيط للنص القادم من النماذج.
    """

    if text is None:
        return ""

    text = str(text).strip()

    return text


# ============================================================
# GREETING DETECTION
# ============================================================

def is_greeting_only(message):
    """
    نكتشف التحية فقط.

    مهم:
    إذا كانت الرسالة تحتوي على تحية + طلب،
    لا نعتبرها تحية فقط.
    """

    text = clean_text(message).lower()

    if not text:
        return False

    greeting_patterns = [
        r"^السلام عليكم[!！,.، ]*$",
        r"^السلام عليكم ورحمة الله وبركاته[!！,.، ]*$",
        r"^سلام عليكم[!！,.، ]*$",
        r"^مرحبا[!！,.، ]*$",
        r"^مرحباً[!！,.، ]*$",
        r"^اهلا[!！,.، ]*$",
        r"^أهلا[!！,.، ]*$",
        r"^اهلا وسهلا[!！,.، ]*$",
        r"^أهلاً وسهلاً[!！,.، ]*$",
    ]

    for pattern in greeting_patterns:

        if re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

def is_image_request(message):
    """
    اكتشاف طلبات إنشاء / توليد / رسم / تعديل الصور.

    هذه الدالة مهمة جدًا حتى لا نرسل طلب الصورة
    إلى Groq كنص عادي.
    """

    text = clean_text(message).lower()

    if not text:
        return False

    image_words = [

        # Arabic
        "صورة",
        "صور",
        "الصورة",
        "ارسم",
        "ارسم لي",
        "أنشئ صورة",
        "انشئ صورة",
        "أنشئ لي صورة",
        "انشئ لي صورة",
        "ولد صورة",
        "ولّد صورة",
        "توليد صورة",
        "إنشاء صورة",
        "انشاء صورة",
        "اصنع صورة",
        "اعمل صورة",
        "اعطني صورة",
        "أعطني صورة",
        "صمم صورة",
        "صمم لي صورة",
        "عدل الصورة",
        "عدّل الصورة",
        "تعديل الصورة",
        "غيّر الصورة",
        "غير الصورة",

        # English
        "generate image",
        "generate a image",
        "generate an image",
        "create image",
        "create an image",
        "make image",
        "make an image",
        "draw image",
        "draw an image",
        "edit image",
        "edit the image",
        "create picture",
        "generate picture",
        "make picture",
    ]

    for word in image_words:

        if word in text:
            return True

    return False


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text(message):
    """
    Groq هو العقل الأساسي للنص.
    """

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY غير موجود."
        )

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization":
                f"Bearer {GROQ_API_KEY}",

            "Content-Type":
                "application/json"
        },
        json={
            "model": GROQ_TEXT_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],

            "temperature": 0.7,

            "max_tokens": 4096
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return clean_text(
        data["choices"][0]["message"]["content"]
    )


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_text(message):
    """
    الاحتياطي الثاني للنص.
    """

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY غير موجود."
        )

    response = requests.post(
        OPENROUTER_URL,

        headers={
            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
                "application/json",

            "HTTP-Referer":
                "https://ido-ai-production.up.railway.app",

            "X-Title":
                "Ido AI"
        },

        json={
            "model": OPENROUTER_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],

            "temperature": 0.7
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return clean_text(
        data["choices"][0]["message"]["content"]
    )


# ============================================================
# MISTRAL TEXT
# ============================================================

def mistral_text(message):
    """
    الاحتياطي الثالث للنص.
    """

    if not MISTRAL_API_KEY:
        raise RuntimeError(
            "MISTRAL_API_KEY غير موجود."
        )

    response = requests.post(
        MISTRAL_URL,

        headers={
            "Authorization":
                f"Bearer {MISTRAL_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={
            "model": MISTRAL_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],

            "temperature": 0.7,

            "max_tokens": 4096
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return clean_text(
        data["choices"][0]["message"]["content"]
    )


# ============================================================
# GEMINI TEXT
# ============================================================

def gemini_text(message):
    """
    Gemini كاحتياطي للنص.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY غير موجود."
        )

    url = (
        f"{GEMINI_URL}/models/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    response = requests.post(
        url,

        headers={
            "Content-Type":
                "application/json"
        },

        json={
            "systemInstruction": {
                "parts": [
                    {
                        "text":
                            SYSTEM_PROMPT
                    }
                ]
            },

            "contents": [
                {
                    "role": "user",

                    "parts": [
                        {
                            "text":
                                message
                        }
                    ]
                }
            ]
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    parts = (
        data
        .get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )

    text_parts = []

    for part in parts:

        if "text" in part:

            text_parts.append(
                part["text"]
            )

    return clean_text(
        "\n".join(text_parts)
    )


# ============================================================
# XAI TEXT
# ============================================================

def xai_text(message):
    """
    XAI كاحتياطي للنص.
    """

    if not XAI_API_KEY:
        raise RuntimeError(
            "XAI_API_KEY غير موجود."
        )

    response = requests.post(
        XAI_URL,

        headers={
            "Authorization":
                f"Bearer {XAI_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={
            "model": XAI_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],

            "temperature": 0.7
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return clean_text(
        data["choices"][0]["message"]["content"]
    )


# ============================================================
# POLLINATIONS TEXT FALLBACK
# ============================================================

def pollinations_text(message):
    """
    احتياطي أخير للنص.
    """

    url = "https://text.pollinations.ai/"

    response = requests.post(
        url,

        json={
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        },

        timeout=120
    )

    response.raise_for_status()

    return clean_text(
        response.text
    )


# ============================================================
# GROQ VISION
# ============================================================

def groq_vision(
    message,
    image_bytes,
    mime_type
):
    """
    Groq Vision:
    يستقبل الصورة ويحللها ويرجع نصًا.

    لا يقوم بتوليد الصورة.
    """

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY غير موجود."
        )

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_url = (
        f"data:{mime_type};base64,"
        f"{encoded_image}"
    )

    response = requests.post(
        GROQ_URL,

        headers={
            "Authorization":
                f"Bearer {GROQ_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={
            "model":
                GROQ_VISION_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content":
                        SYSTEM_PROMPT
                },

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text":
                                message
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url":
                                    image_url
                            }
                        }
                    ]
                }
            ],

            "temperature": 0.4,

            "max_tokens": 4096
        },

        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return clean_text(
        data["choices"][0]["message"]["content"]
    )


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def gemini_image(
    prompt,
    image_bytes=None,
    mime_type=None
):
    """
    Gemini هو مولد الصور الأساسي.

    يدعم:
        - إنشاء صورة من النص
        - تعديل صورة موجودة
        - نص + صورة
        - إخراج صورة

    النتيجة:
        IMAGE_DATA:<base64>
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY غير موجود."
        )

    url = (
        f"{GEMINI_URL}/models/"
        f"{GEMINI_IMAGE_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    parts = [
        {
            "text": prompt
        }
    ]


    # --------------------------------------------------------
    # إذا كانت هناك صورة، نرسلها إلى Gemini أيضًا
    # --------------------------------------------------------

    if image_bytes:

        if not mime_type:

            mime_type = (
                mimetypes.guess_type(
                    "image.jpg"
                )[0]
                or "image/jpeg"
            )

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        parts.append(
            {
                "inline_data": {
                    "mime_type":
                        mime_type,

                    "data":
                        encoded_image
                }
            }
        )


    # --------------------------------------------------------
    # Gemini Image Request
    # --------------------------------------------------------

    response = requests.post(
        url,

        headers={
            "Content-Type":
                "application/json"
        },

        json={
            "contents": [
                {
                    "role": "user",

                    "parts":
                        parts
                }
            ],

            "generationConfig": {

                "responseModalities": [
                    "TEXT",
                    "IMAGE"
                ]
            }
        },

        timeout=180
    )

    response.raise_for_status()

    data = response.json()


    # --------------------------------------------------------
    # استخراج النتيجة
    # --------------------------------------------------------

    candidates = data.get(
        "candidates",
        []
    )

    if not candidates:

        raise RuntimeError(
            "Gemini لم يُرجع أي نتيجة."
        )


    response_parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )


    generated_text = []

    generated_image = None


    for part in response_parts:

        # ------------------------------
        # نص
        # ------------------------------

        if "text" in part:

            generated_text.append(
                part["text"]
            )


        # ------------------------------
        # صورة
        # ------------------------------

        inline_data = (
            part.get("inlineData")
            or part.get("inline_data")
        )

        if inline_data:

            image_data = inline_data.get(
                "data"
            )

            image_mime = inline_data.get(
                "mimeType"
            ) or inline_data.get(
                "mime_type"
            ) or "image/png"

            if image_data:

                generated_image = (
                    f"data:{image_mime};base64,"
                    f"{image_data}"
                )


    # --------------------------------------------------------
    # إذا حصلنا على صورة
    # --------------------------------------------------------

    if generated_image:

        return {
            "imageUrl":
                generated_image,

            "answer":
                clean_text(
                    "\n".join(
                        generated_text
                    )
                ),

            "provider":
                "Gemini",

            "type":
                "image"
        }


    # --------------------------------------------------------
    # Gemini لم يُرجع صورة
    # --------------------------------------------------------

    text = clean_text(
        "\n".join(
            generated_text
        )
    )

    raise RuntimeError(
        "Gemini لم يُرجع صورة. "
        f"النص الناتج: {text}"
    )


# ============================================================
# IMAGE RESPONSE
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type="image/jpeg",
    conversation_id=None
):
    """
    المسار الرئيسي للصور.

    الحالة 1:
        المستخدم رفع صورة ويريد تحليلها.

        Groq Vision
        ↓

        نص تحليلي

    الحالة 2:
        المستخدم يريد إنشاء صورة.

        Gemini Image
        ↓

        صورة

    الحالة 3:
        المستخدم رفع صورة وطلب تعديلها.

        Gemini Image
        ↓

        صورة جديدة
    """

    message = clean_text(message)


    print()
    print("=" * 70)
    print("IMAGE REQUEST")
    print("=" * 70)

    print(
        "MESSAGE:",
        message
    )

    print(
        "IMAGE RECEIVED:",
        bool(image_bytes)
    )

    print(
        "MIME TYPE:",
        mime_type
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )


    # ========================================================
    # إنشاء / تعديل صورة
    # ========================================================

    if is_image_request(message):

        print()
        print(
            "IMAGE MODE: GENERATION / EDITING"
        )

        print(
            "PRIMARY IMAGE AI: GEMINI"
        )


        try:

            result = gemini_image(
                prompt=message,
                image_bytes=image_bytes,
                mime_type=mime_type
            )

            print(
                "GEMINI IMAGE: SUCCESS"
            )

            print(
                "PROVIDER: Gemini"
            )

            print("=" * 70)

            return result


        except Exception as e:

            print(
                "GEMINI IMAGE ERROR:",
                repr(e)
            )

            print(
                "IMAGE GENERATION FAILED"
            )

            print("=" * 70)

            return {
                "answer":
                    "تعذر إنشاء الصورة حاليًا. "
                    "تأكد من أن GEMINI_API_KEY "
                    "صحيح وأن نموذج الصور متاح.",

                "imageUrl":
                    "",

                "provider":
                    "Gemini",

                "type":
                    "image_error"
            }


    # ========================================================
    # تحليل صورة
    # ========================================================

    if image_bytes:

        print()
        print(
            "IMAGE MODE: VISION ANALYSIS"
        )

        print(
            "PRIMARY VISION AI: GROQ"
        )


        try:

            answer = groq_vision(
                message=(
                    message
                    or
                    "حلل هذه الصورة بالتفصيل."
                ),

                image_bytes=
                    image_bytes,

                mime_type=
                    mime_type
            )

            print(
                "GROQ VISION: SUCCESS"
            )

            print(
                "PROVIDER: Groq Vision"
            )

            print("=" * 70)

            return {
                "answer":
                    answer,

                "imageUrl":
                    "",

                "provider":
                    "Groq Vision",

                "type":
                    "vision"
            }


        except Exception as e:

            print(
                "GROQ VISION ERROR:",
                repr(e)
            )

            # ---------------------------------------------
            # إذا فشل Groq Vision، نحاول Gemini
            # ---------------------------------------------

            print(
                "TRYING GEMINI VISION..."
            )

            try:

                result = gemini_image(
                    prompt=(
                        message
                        or
                        "حلل هذه الصورة."
                    ),

                    image_bytes=
                        image_bytes,

                    mime_type=
                        mime_type
                )

                return result


            except Exception as second_error:

                print(
                    "GEMINI VISION ERROR:",
                    repr(second_error)
                )

                return {
                    "answer":
                        "تعذر تحليل الصورة حاليًا.",

                    "imageUrl":
                        "",

                    "provider":
                        "Vision",

                    "type":
                        "vision_error"
                }


    # ========================================================
    # لا صورة ولا طلب صورة
    # ========================================================

    return {
        "answer":
            "لم يتم إرسال صورة صالحة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(message):
    """
    استجابة سريعة متوافقة مع app.py والنسخ القديمة.
    """

    message = clean_text(message)

    if not message:

        return (
            "اكتب رسالة أولًا."
        )


    # --------------------------------------------------------
    # تحية فقط
    # --------------------------------------------------------

    if is_greeting_only(message):

        return (
            "وعليكم السلام ورحمة الله وبركاته! "
            "كيف يمكنني مساعدتك؟"
        )


    # --------------------------------------------------------
    # النص الأساسي
    # --------------------------------------------------------

    return get_response(
        message
    )


# ============================================================
# GET RESPONSE
# ============================================================

def get_response(
    message,
    conversation_id=None
):
    """
    العقل الأساسي للنص.

    الترتيب:

        GROQ
          ↓
        OPENROUTER
          ↓
        MISTRAL
          ↓
        GEMINI
          ↓
        XAI
          ↓
        POLLINATIONS
    """

    message = clean_text(message)


    if not message:

        return {
            "answer":
                "اكتب رسالة أولًا.",

            "imageUrl":
                "",

            "provider":
                None
        }


    print()
    print("=" * 70)
    print("DYNAMIC AI RESPONSE")
    print("=" * 70)

    print(
        "MESSAGE:",
        message
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )


    # ========================================================
    # منع إرسال طلبات الصور إلى مسار النص
    # ========================================================

    if is_image_request(message):

        print(
            "IMAGE REQUEST DETECTED"
        )

        print(
            "REDIRECTING TO GEMINI IMAGE"
        )

        result = get_image_response(
            message,
            image_bytes=None,
            mime_type="image/jpeg",
            conversation_id=conversation_id
        )

        return result


    # ========================================================
    # التحية فقط
    # ========================================================

    if is_greeting_only(message):

        return {
            "answer":
                "وعليكم السلام ورحمة الله وبركاته! "
                "كيف يمكنني مساعدتك؟",

            "imageUrl":
                "",

            "provider":
                "Ido AI"
        }


    # ========================================================
    # 1. GROQ
    # ========================================================

    try:

        if GROQ_API_KEY:

            print(
                "TRYING GROQ..."
            )

            answer = groq_text(
                message
            )

            if answer:

                print(
                    "GROQ: SUCCESS"
                )

                return {
                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "Groq"
                }


    except Exception as e:

        print(
            "GROQ ERROR:",
            repr(e)
        )


    # ========================================================
    # 2. OPENROUTER
    # ========================================================

    try:

        if OPENROUTER_API_KEY:

            print(
                "TRYING OPENROUTER..."
            )

            answer = openrouter_text(
                message
            )

            if answer:

                print(
                    "OPENROUTER: SUCCESS"
                )

                return {
                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "OpenRouter"
                }


    except Exception as e:

        print(
            "OPENROUTER ERROR:",
            repr(e)
        )


    # ========================================================
    # 3. MISTRAL
    # ========================================================

    try:

        if MISTRAL_API_KEY:

            print(
                "TRYING MISTRAL..."
            )

            answer = mistral_text(
                message
            )

            if answer:

                print(
                    "MISTRAL: SUCCESS"
                )

                return {
                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "Mistral"
                }


    except Exception as e:

        print(
            "MISTRAL ERROR:",
            repr(e)
        )


    # ========================================================
    # 4. GEMINI TEXT
    # ========================================================

    try:

        if GEMINI_API_KEY:

            print(
                "TRYING GEMINI TEXT..."
            )

            answer = gemini_text(
                message
            )

            if answer:

                print(
                    "GEMINI: SUCCESS"
                )

                return {
                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "Gemini"
                }


    except Exception as e:

        print(
            "GEMINI TEXT ERROR:",
            repr(e)
        )


    # ========================================================
    # 5. XAI
    # ========================================================

    try:

        if XAI_API_KEY:

            print(
                "TRYING XAI..."
            )

            answer = xai_text(
                message
            )

            if answer:

                print(
                    "XAI: SUCCESS"
                )

                return {
                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "XAI"
                }


    except Exception as e:

        print(
            "XAI ERROR:",
            repr(e)
        )


    # ========================================================
    # 6. POLLINATIONS
    # ========================================================

    try:

        print(
            "TRYING POLLINATIONS..."
        )

        answer = pollinations_text(
            message
        )

        if answer:

            print(
                "POLLINATIONS: SUCCESS"
            )

            return {
                "answer":
                    answer,

                "imageUrl":
                    "",

                "provider":
                    "Pollinations"
            }


    except Exception as e:

        print(
            "POLLINATIONS ERROR:",
            repr(e)
        )


    # ========================================================
    # ALL FAILED
    # ========================================================

    print(
        "ALL AI PROVIDERS FAILED"
    )

    print("=" * 70)


    return {
        "answer":
            "عذرًا، حدث خطأ أثناء الاتصال "
            "بخدمات الذكاء الاصطناعي. "
            "حاول مرة أخرى.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# COMPATIBILITY
# ============================================================

print()
print(
    "COMPATIBILITY: quick_response available"
)

print(
    "COMPATIBILITY: "
    "get_response(message, conversation_id=None)"
)

print(
    "COMPATIBILITY: "
    "get_image_response("
    "message, image_bytes, mime_type, "
    "conversation_id=None)"
)

print("=" * 70)

print(
    "PRIMARY AI:"
)

print(
    "    GROQ"
)

print(
    "TEXT ROUTE:"
)

print(
    "    GROQ -> OPENROUTER -> MISTRAL "
    "-> GEMINI -> XAI -> POLLINATIONS"
)

print(
    "VISION ROUTE:"
)

print(
    "    GROQ VISION"
)

print(
    "IMAGE GENERATION:"
)

print(
    "    GEMINI IMAGE"
)

print(
    "GEMINI IMAGE MODEL:"
)

print(
    f"    {GEMINI_IMAGE_MODEL}"
)

print(
    "GREETING:"
)

print(
    "    DIRECT RESPONSE"
)

print("=" * 70)