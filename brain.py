# ============================================================
# Ido AI - Unified AI Brain
# ============================================================
#
# PRIMARY TEXT AI:
#     Groq
#
# TEXT FALLBACKS:
#     Mistral
#     OpenRouter
#     xAI
#     Pollinations
#
# IMAGE ANALYSIS:
#     Groq Vision
#     -> Mistral Vision
#     -> OpenRouter Vision
#
# IMAGE GENERATION:
#     Gemini
#     -> Pollinations
#     -> OpenRouter
#
# IMPORTANT:
#     Image requests NEVER go through the normal text route.
#
# Compatible with:
#     app.py
#     api.py
#
# ============================================================

import os
import base64
import time
import requests

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


CONNECT_TIMEOUT = float(
    os.getenv(
        "REQUEST_CONNECT_TIMEOUT",
        "5"
    )
)

READ_TIMEOUT = float(
    os.getenv(
        "REQUEST_READ_TIMEOUT",
        "60"
    )
)

REQUEST_TIMEOUT = (
    CONNECT_TIMEOUT,
    READ_TIMEOUT
)


CIRCUIT_BREAK_SECONDS = int(
    os.getenv(
        "PROVIDER_COOLDOWN_SECONDS",
        "300"
    )
)


_provider_disabled_until = {}


# ============================================================
# SAFE PROVIDER CONTROL
# ============================================================

def provider_available(name):
    until = _provider_disabled_until.get(
        name,
        0
    )

    return time.time() >= until


def disable_provider(
    name,
    reason="temporary failure"
):
    _provider_disabled_until[name] = (
        time.time()
        + CIRCUIT_BREAK_SECONDS
    )

    print(
        f"{name}: TEMPORARILY SKIPPED "
        f"for {CIRCUIT_BREAK_SECONDS}s "
        f"({reason})"
    )


def provider_failure(
    name,
    status_code=None
):
    if status_code in (
        401,
        403,
        429
    ):
        disable_provider(
            name,
            f"HTTP {status_code}"
        )


# ============================================================
# SAFE HELPERS
# ============================================================

def clean_answer(value):

    if value is None:
        return None

    try:
        value = str(value).strip()

    except Exception:
        return None

    return value or None


def request_json(
    response,
    provider
):

    try:
        return response.json()

    except Exception as exc:

        print(
            f"{provider}: INVALID JSON:",
            exc
        )

        print(
            f"{provider}: BODY:",
            response.text[:1500]
        )

        return None


# ============================================================
# API KEYS
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

XAI_API_KEY = os.getenv(
    "XAI_API_KEY"
)

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# ============================================================
# MODELS
# ============================================================

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest"
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "pixtral-12b-2409"
)


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-image-1"
)


XAI_MODEL = os.getenv(
    "XAI_MODEL",
    "grok-4.5"
)


POLLINATIONS_TEXT_MODEL = os.getenv(
    "POLLINATIONS_TEXT_MODEL",
    "openai"
)

POLLINATIONS_IMAGE_MODEL = os.getenv(
    "POLLINATIONS_IMAGE_MODEL",
    "flux"
)


GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-2.5-flash-image"
)


# ============================================================
# ENDPOINTS
# ============================================================

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)


XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)


POLLINATIONS_CHAT_URL = (
    "https://gen.pollinations.ai/v1/chat/completions"
)


POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/image/"
)


# ============================================================
# STARTUP STATUS
# ============================================================

print("=" * 60)
print("IDO AI BRAIN.PY LOADED")
print("=" * 60)

if GROQ_API_KEY:
    print("GROQ CLIENT: READY")
    print("GROQ TEXT MODEL:", GROQ_MODEL)
    print("GROQ VISION MODEL:", GROQ_VISION_MODEL)
else:
    print("GROQ_API_KEY: NOT FOUND")


if MISTRAL_API_KEY:
    print("MISTRAL CLIENT: READY")
else:
    print("MISTRAL_API_KEY: NOT FOUND")


if OPENROUTER_API_KEY:
    print("OPENROUTER CLIENT: READY")
else:
    print("OPENROUTER_API_KEY: NOT FOUND")


if XAI_API_KEY:
    print("XAI CLIENT: READY")
else:
    print("XAI_API_KEY: NOT FOUND")


if POLLINATIONS_API_KEY:
    print("POLLINATIONS CLIENT: READY")
else:
    print("POLLINATIONS_API_KEY: NOT FOUND")


if GEMINI_API_KEY:
    print("GEMINI CLIENT: READY")
    print("GEMINI IMAGE MODEL:", GEMINI_IMAGE_MODEL)
else:
    print("GEMINI_API_KEY: NOT FOUND")


print("=" * 60)


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def generate_image_gemini(prompt):

    if not GEMINI_API_KEY:
        print(
            "GEMINI IMAGE: API KEY NOT FOUND"
        )
        return None

    if not provider_available(
        "GEMINI_IMAGE"
    ):
        return None

    try:

        print("=" * 45)
        print("GEMINI IMAGE GENERATION STARTED")
        print(
            "GEMINI IMAGE MODEL:",
            GEMINI_IMAGE_MODEL
        )

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/"
            f"{GEMINI_IMAGE_MODEL}:generateContent"
        )

        response = requests.post(

            url,

            params={
                "key": GEMINI_API_KEY
            },

            headers={
                "Content-Type":
                    "application/json"
            },

            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text":
                                    prompt
                            }
                        ]
                    }
                ],

                "generationConfig": {
                    "responseModalities": [
                        "TEXT",
                        "IMAGE"
                    ]
                }
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "GEMINI IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "GEMINI IMAGE RESPONSE:",
                response.text[:2000]
            )

            provider_failure(
                "GEMINI_IMAGE",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Gemini Image"
        )

        if not data:
            return None

        candidates = data.get(
            "candidates",
            []
        )

        if not candidates:
            return None

        content = candidates[0].get(
            "content",
            {}
        )

        parts = content.get(
            "parts",
            []
        )

        for part in parts:

            inline_data = part.get(
                "inlineData"
            )

            if not inline_data:
                continue

            mime_type = inline_data.get(
                "mimeType",
                "image/png"
            )

            image_base64 = inline_data.get(
                "data"
            )

            if image_base64:

                image_url = (
                    f"data:{mime_type};base64,"
                    f"{image_base64}"
                )

                print(
                    "GEMINI IMAGE: SUCCESS"
                )

                return image_url

        print(
            "GEMINI IMAGE: NO IMAGE RETURNED"
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "GEMINI IMAGE: TIMEOUT"
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "GEMINI IMAGE: CONNECTION ERROR"
        )

        return None

    except Exception as exc:

        print(
            "GEMINI IMAGE ERROR:",
            exc
        )

        return None


# ============================================================
# GROQ TEXT
# ============================================================

def ask_groq(message):

    if not GROQ_API_KEY:
        return None

    if not message:
        return None

    if not provider_available(
        "GROQ"
    ):
        return None

    try:

        print(
            "Trying Groq..."
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
                    GROQ_MODEL,

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            message
                    }
                ],

                "temperature":
                    0.7,

                "max_completion_tokens":
                    2048
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq Response:",
                response.text[:1500]
            )

            provider_failure(
                "GROQ",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Groq"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        answer = clean_answer(
            content
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "Groq ERROR: timeout"
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: connection failed"
        )

        return None

    except Exception as exc:

        print(
            "Groq ERROR:",
            exc
        )

        return None


# ============================================================
# MISTRAL TEXT
# ============================================================

def ask_mistral(message):

    if not MISTRAL_API_KEY:
        return None

    if not message:
        return None

    if not provider_available(
        "MISTRAL"
    ):
        return None

    try:

        print(
            "Trying Mistral..."
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
                "model":
                    MISTRAL_MODEL,

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            message
                    }
                ],

                "temperature":
                    0.7,

                "max_tokens":
                    2048
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral Response:",
                response.text[:1500]
            )

            provider_failure(
                "MISTRAL",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Mistral"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "Mistral ERROR:",
            exc
        )

        return None


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_headers():

    return {
        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "X-Title":
            "Ido AI"
    }


def ask_openrouter(message):

    if not OPENROUTER_API_KEY:
        return None

    if not message:
        return None

    if not provider_available(
        "OPENROUTER"
    ):
        return None

    try:

        print(
            "Trying OpenRouter..."
        )

        response = requests.post(

            OPENROUTER_CHAT_URL,

            headers=openrouter_headers(),

            json={
                "model":
                    OPENROUTER_TEXT_MODEL,

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
                response.text[:1500]
            )

            provider_failure(
                "OPENROUTER",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "OpenRouter ERROR:",
            exc
        )

        return None


# ============================================================
# XAI TEXT
# ============================================================

def ask_xai(message):

    if not XAI_API_KEY:
        return None

    if not message:
        return None

    if not provider_available(
        "XAI"
    ):
        return None

    try:

        print(
            "Trying xAI..."
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
                "model":
                    XAI_MODEL,

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            message
                    }
                ],

                "temperature":
                    0.7
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI Response:",
                response.text[:1500]
            )

            provider_failure(
                "XAI",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "xAI ERROR:",
            exc
        )

        return None


# ============================================================
# POLLINATIONS TEXT
# ============================================================

def ask_pollinations(message):

    if not POLLINATIONS_API_KEY:
        return None

    if not message:
        return None

    if not provider_available(
        "POLLINATIONS"
    ):
        return None

    try:

        print(
            "Trying Pollinations..."
        )

        response = requests.post(

            POLLINATIONS_CHAT_URL,

            headers={
                "Authorization":
                    f"Bearer {POLLINATIONS_API_KEY}",

                "Content-Type":
                    "application/json"
            },

            json={
                "model":
                    POLLINATIONS_TEXT_MODEL,

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
            "Pollinations Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Pollinations Response:",
                response.text[:1500]
            )

            provider_failure(
                "POLLINATIONS",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Pollinations"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "Pollinations ERROR:",
            exc
        )

        return None


# ============================================================
# POLLINATIONS IMAGE
# ============================================================

def generate_image_pollinations(prompt):

    if not POLLINATIONS_API_KEY:
        return None

    if not provider_available(
        "POLLINATIONS_IMAGE"
    ):
        return None

    try:

        print("=" * 45)
        print(
            "POLLINATIONS IMAGE GENERATION STARTED"
        )

        response = requests.get(

            POLLINATIONS_IMAGE_URL
            + requests.utils.quote(
                prompt,
                safe=""
            ),

            headers={
                "Authorization":
                    f"Bearer {POLLINATIONS_API_KEY}"
            },

            params={
                "model":
                    POLLINATIONS_IMAGE_MODEL,

                "width":
                    1024,

                "height":
                    1024,

                "n":
                    1
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Pollinations IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Pollinations IMAGE RESPONSE:",
                response.text[:1500]
            )

            provider_failure(
                "POLLINATIONS_IMAGE",
                response.status_code
            )

            return None

        content_type = (
            response.headers.get(
                "Content-Type",
                "image/png"
            )
        )

        encoded = base64.b64encode(
            response.content
        ).decode(
            "utf-8"
        )

        image_url = (
            f"data:{content_type};base64,"
            f"{encoded}"
        )

        print(
            "POLLINATIONS IMAGE: SUCCESS"
        )

        return image_url

    except Exception as exc:

        print(
            "Pollinations IMAGE ERROR:",
            exc
        )

        return None


# ============================================================
# OPENROUTER IMAGE
# ============================================================

def generate_image_openrouter(prompt):

    if not OPENROUTER_API_KEY:
        return None

    if not provider_available(
        "OPENROUTER_IMAGE"
    ):
        return None

    try:

        print("=" * 45)
        print(
            "OPENROUTER IMAGE GENERATION STARTED"
        )

        response = requests.post(

            OPENROUTER_IMAGE_URL,

            headers=openrouter_headers(),

            json={
                "model":
                    OPENROUTER_IMAGE_MODEL,

                "prompt":
                    prompt,

                "n":
                    1
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter IMAGE RESPONSE:",
                response.text[:1500]
            )

            provider_failure(
                "OPENROUTER_IMAGE",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter IMAGE"
        )

        if not data:
            return None

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        item = items[0]

        b64 = item.get(
            "b64_json"
        )

        if b64:

            media_type = item.get(
                "media_type",
                "image/png"
            )

            return (
                f"data:{media_type};base64,"
                f"{b64}"
            )

        image_url = item.get(
            "url"
        )

        if image_url:
            return image_url

        return None

    except Exception as exc:

        print(
            "OpenRouter IMAGE ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE GENERATION ROUTER
# ============================================================

def generate_image(prompt):

    prompt = clean_answer(
        prompt
    )

    if not prompt:

        return {
            "answer":
                "اكتب وصف الصورة التي تريد إنشاءها.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)
    print("IMAGE GENERATION REQUEST")
    print("PROMPT:", prompt)
    print("=" * 60)

    # --------------------------------------------------------
    # 1. GEMINI
    # --------------------------------------------------------

    image = generate_image_gemini(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة Gemini.",

            "imageUrl":
                image,

            "provider":
                "Gemini"
        }

    print(
        "Gemini image failed."
    )

    # --------------------------------------------------------
    # 2. POLLINATIONS
    # --------------------------------------------------------

    image = generate_image_pollinations(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة Pollinations.",

            "imageUrl":
                image,

            "provider":
                "Pollinations"
        }

    print(
        "Pollinations image failed."
    )

    # --------------------------------------------------------
    # 3. OPENROUTER
    # --------------------------------------------------------

    image = generate_image_openrouter(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة OpenRouter.",

            "imageUrl":
                image,

            "provider":
                "OpenRouter"
        }

    # --------------------------------------------------------
    # FINAL FAILURE
    # --------------------------------------------------------

    print(
        "ALL IMAGE PROVIDERS FAILED."
    )

    return {
        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تحقق من إعدادات مولدات الصور "
            "ومفاتيح API.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_WORDS = [

    "أنشئ صورة",
    "انشئ صورة",
    "أنشئ لي صورة",
    "انشئ لي صورة",

    "اصنع صورة",
    "اصنع لي صورة",

    "إنشاء صورة",
    "انشاء صورة",

    "ولد صورة",
    "ولّد صورة",

    "ارسم صورة",
    "ارسم لي",

    "صمم صورة",
    "صمم لي صورة",

    "اعمل صورة",
    "اعمل لي صورة",

    "صورة لي",

    "generate an image",
    "generate image",

    "create an image",
    "create image",

    "make an image",
    "make image",

    "draw an image",
    "draw image",

    "generate a picture",
    "create a picture",
    "make a picture"
]


def is_image_generation_request(
    message
):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    return any(
        word.lower() in text
        for word in IMAGE_WORDS
    )


# ============================================================
# EXTRACT IMAGE PROMPT
# ============================================================

def get_image_prompt(
    message
):

    if not message:
        return ""

    text = str(
        message
    ).strip()

    prefixes = [

        "أنشئ لي صورة",
        "أنشئ صورة",

        "انشئ لي صورة",
        "انشئ صورة",

        "اصنع لي صورة",
        "اصنع صورة",

        "إنشاء صورة",
        "انشاء صورة",

        "ولد صورة",
        "ولّد صورة",

        "ارسم لي",
        "ارسم صورة",

        "صمم لي صورة",
        "صمم صورة",

        "اعمل لي صورة",
        "اعمل صورة",

        "generate an image of",
        "generate image of",

        "create an image of",
        "create image of",

        "make an image of",
        "make image of",

        "draw an image of",

        "generate a picture of",
        "create a picture of",
        "make a picture of"
    ]

    lower = text.lower()

    for prefix in prefixes:

        if lower.startswith(
            prefix.lower()
        ):

            return text[
                len(prefix):
            ].strip()

    return text


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_WORDS = [

    "السلام عليكم",
    "السلام عليكم ورحمة الله وبركاته",

    "سلام عليكم",

    "مرحبا",
    "مرحبًا",

    "اهلا",
    "أهلا",

    "أهلًا",
    "اهلاً",

    "السلام"
]


def contains_greeting(
    message
):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    return any(
        greeting.lower() in text
        for greeting in GREETING_WORDS
    )


# ============================================================
# QUICK RESPONSES
#
# IMPORTANT:
# Do NOT use these for messages containing a real question.
# ============================================================

QUICK_RESPONSES = {

    "hello":
        "السلام عليكم ورحمة الله وبركاته. "
        "أنا Ido AI، كيف يمكنني مساعدتك؟",

    "hi":
        "السلام عليكم ورحمة الله وبركاته. "
        "أنا Ido AI، كيف يمكنني مساعدتك؟",

    "مرحبا":
        "أهلًا وسهلًا بك. كيف يمكنني مساعدتك؟",

    "مرحبًا":
        "أهلًا وسهلًا بك. كيف يمكنني مساعدتك؟",

    "شكرا":
        "على الرحب والسعة.",

    "شكراً":
        "العفو، يسعدني مساعدتك.",

    "وداعا":
        "إلى اللقاء! أتمنى لك يومًا سعيدًا."
}


def quick_response(
    message
):

    if not message:
        return None

    try:

        text = str(
            message
        ).strip().lower()

    except Exception:

        return None

    if not text:
        return None

    # --------------------------------------------------------
    # إذا كانت الرسالة تحتوي على تحية مع سؤال أو طلب،
    # لا نستخدم الرد الثابت.
    #
    # مثال:
    # "السلام عليكم اشرح لي بايثون"
    #
    # تذهب إلى Groq.
    # --------------------------------------------------------

    if contains_greeting(
        text
    ):

        words_after_greeting = text

        for greeting in GREETING_WORDS:

            words_after_greeting = (
                words_after_greeting.replace(
                    greeting.lower(),
                    ""
                )
            )

        words_after_greeting = (
            words_after_greeting
            .strip(" ,،.!؟?!")
        )

        if words_after_greeting:

            return None

        return (
            "وعليكم السلام ورحمة الله وبركاته. "
            "كيف يمكنني مساعدتك؟"
        )

    # --------------------------------------------------------
    # الردود القصيرة فقط
    # --------------------------------------------------------

    for key, value in QUICK_RESPONSES.items():

        if text == key.lower():

            return value

    return None


# ============================================================
# MAIN TEXT ROUTER
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    if not message:

        return "اكتب رسالة أولًا."

    original_message = str(
        message
    ).strip()

    if not original_message:

        return "اكتب رسالة أولًا."

    print("=" * 60)
    print("DYNAMIC AI RESPONSE")
    print("MESSAGE:", original_message)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 60)

    # ========================================================
    # IMAGE REQUEST MUST BE FIRST
    # ========================================================

    if is_image_generation_request(
        original_message
    ):

        print(
            "IMAGE REQUEST DETECTED"
        )

        prompt = get_image_prompt(
            original_message
        )

        print(
            "IMAGE PROMPT:",
            prompt
        )

        return generate_image(
            prompt
        )

    # ========================================================
    # QUICK RESPONSE
    # ========================================================

    quick = quick_response(
        original_message
    )

    if quick:

        print(
            "QUICK RESPONSE SUCCESS"
        )

        return quick

    # ========================================================
    # PRIMARY AI = GROQ
    # ========================================================

    routes = [

        (
            "GROQ",
            ask_groq
        ),

        (
            "MISTRAL",
            ask_mistral
        ),

        (
            "OPENROUTER",
            ask_openrouter
        ),

        (
            "XAI",
            ask_xai
        ),

        (
            "POLLINATIONS",
            ask_pollinations
        )
    ]

    for name, function in routes:

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(temporary cooldown)"
            )

            continue

        try:

            answer = function(
                original_message
            )

        except Exception as exc:

            print(
                f"{name} ROUTER ERROR:",
                exc
            )

            answer = None

        if answer:

            print(
                f"TEXT ROUTE SUCCESS: {name}"
            )

            return answer

        print(
            f"{name} failed. "
            "Trying next provider..."
        )

    # ========================================================
    # FINAL FALLBACK
    # ========================================================

    return (
        "أنا Ido AI، لكن جميع مزودي الذكاء "
        "الاصطناعي المتاحين فشلوا حاليًا. "
        "تحقق من مفاتيح API والرصيد."
    )


# ============================================================
# GROQ VISION
# ============================================================

def ask_groq_image(
    message,
    image_bytes,
    mime_type
):

    if not GROQ_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "GROQ_VISION"
    ):
        return None

    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_url = (
            f"data:{mime_type};base64,"
            f"{encoded}"
        )

        print(
            "Trying Groq Vision..."
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
                                        image_url
                                }
                            }
                        ]
                    }
                ],

                "max_completion_tokens":
                    2048
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq Vision Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq Vision Response:",
                response.text[:1500]
            )

            provider_failure(
                "GROQ_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Groq Vision"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        answer = clean_answer(
            content
        )

        if answer:

            print(
                "VISION ROUTE SUCCESS: GROQ_VISION"
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Groq Vision ERROR:",
            exc
        )

        return None


# ============================================================
# MISTRAL VISION
# ============================================================

def ask_mistral_image(
    message,
    image_bytes,
    mime_type
):

    if not MISTRAL_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "MISTRAL_VISION"
    ):
        return None

    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_url = (
            f"data:{mime_type};base64,"
            f"{encoded}"
        )

        print(
            "Trying Mistral Vision..."
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
                "model":
                    MISTRAL_VISION_MODEL,

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
                                        image_url
                                }
                            }
                        ]
                    }
                ],

                "max_tokens":
                    2048
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral Vision Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral Vision Response:",
                response.text[:1500]
            )

            provider_failure(
                "MISTRAL_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Mistral Vision"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "Mistral Vision ERROR:",
            exc
        )

        return None


# ============================================================
# OPENROUTER VISION
# ============================================================

def ask_openrouter_image(
    message,
    image_bytes,
    mime_type
):

    if not OPENROUTER_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "OPENROUTER_VISION"
    ):
        return None

    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_url = (
            f"data:{mime_type};base64,"
            f"{encoded}"
        )

        print(
            "Trying OpenRouter Vision..."
        )

        response = requests.post(

            OPENROUTER_CHAT_URL,

            headers=openrouter_headers(),

            json={
                "model":
                    OPENROUTER_VISION_MODEL,

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
                                        image_url
                                }
                            }
                        ]
                    }
                ]
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter Vision Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter Vision Response:",
                response.text[:1500]
            )

            provider_failure(
                "OPENROUTER_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter Vision"
        )

        if not data:
            return None

        choices = data.get(
            "choices",
            []
        )

        if not choices:
            return None

        content = (
            choices[0]
            .get(
                "message",
                {}
            )
            .get(
                "content"
            )
        )

        return clean_answer(
            content
        )

    except Exception as exc:

        print(
            "OpenRouter Vision ERROR:",
            exc
        )

        return None


# ============================================================
# MAIN IMAGE ANALYSIS ROUTER
# ============================================================

def get_image_response(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
):

    if not image_bytes:

        return (
            "لم يتم إرسال صورة صالحة."
        )

    if not mime_type:

        mime_type = "image/jpeg"

    if not mime_type.startswith(
        "image/"
    ):

        return (
            "الملف المرسل ليس صورة صالحة."
        )

    if not message:

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    message = str(
        message
    ).strip()

    print("=" * 60)
    print("IMAGE ANALYSIS REQUEST")
    print("CONVERSATION ID:", conversation_id)
    print("=" * 60)

    routes = [

        (
            "GROQ_VISION",
            ask_groq_image
        ),

        (
            "MISTRAL_VISION",
            ask_mistral_image
        ),

        (
            "OPENROUTER_VISION",
            ask_openrouter_image
        )
    ]

    for name, function in routes:

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(temporary cooldown)"
            )

            continue

        try:

            answer = function(

                message,

                image_bytes,

                mime_type
            )

        except Exception as exc:

            print(
                f"{name} ERROR:",
                exc
            )

            answer = None

        if answer:

            print(
                f"VISION ROUTE SUCCESS: {name}"
            )

            return answer

    return (
        "تعذر تحليل الصورة حاليًا. "
        "تحقق من مفاتيح مزودي الرؤية."
    )


# ============================================================
# COMPATIBILITY
# ============================================================

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

print("=" * 60)
print("PRIMARY AI: GROQ")
print(
    "TEXT ROUTE: "
    "GROQ -> MISTRAL -> OPENROUTER -> "
    "XAI -> POLLINATIONS"
)
print(
    "VISION ROUTE: "
    "GROQ VISION -> MISTRAL VISION -> "
    "OPENROUTER VISION"
)
print(
    "IMAGE ROUTE: "
    "GEMINI -> POLLINATIONS -> OPENROUTER"
)
print(
    "IMAGE REQUESTS ARE SEPARATED "
    "FROM TEXT REQUESTS"
)
print("=" * 60)