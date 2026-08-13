# ============================================================
# Ido AI - Unified AI Brain
# ============================================================
#
# PRIMARY AI:
#     GROQ
#
# TEXT:
#     GROQ -> MISTRAL -> OPENROUTER -> GEMINI -> XAI -> POLLINATIONS
#
# IMAGE UNDERSTANDING:
#     GROQ VISION -> GEMINI VISION
#
# IMAGE GENERATION:
#     GROQ understands the request
#             |
#             v
#     GEMINI 3.1 FLASH IMAGE
#
# IMPORTANT:
#     Groq is the PRIMARY AI for understanding and text.
#     Groq is NOT asked to generate an image through Chat API.
#     Gemini is used as the image-generation engine.
#
# ============================================================

import os
import base64
import time
import requests

from dotenv import load_dotenv


# ============================================================
# GEMINI SDK
# ============================================================

try:
    from google import genai
    from google.genai import types

except Exception:
    genai = None
    types = None


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
        "30"
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
# PROVIDER CONTROL
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

        value = str(
            value
        ).strip()

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
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# Gemini native image model.
#
# Current Google image model:
# Gemini 3.1 Flash Image
#
GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)


GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


GEMINI_ENABLED = (
    bool(GEMINI_API_KEY)
    and genai is not None
)


gemini_client = None


if GEMINI_ENABLED:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print(
            "GEMINI CLIENT: READY"
        )

        print(
            "GEMINI TEXT MODEL:",
            GEMINI_TEXT_MODEL
        )

        print(
            "GEMINI IMAGE MODEL:",
            GEMINI_IMAGE_MODEL
        )

    except Exception as exc:

        print(
            "GEMINI CLIENT ERROR:",
            exc
        )

        gemini_client = None

else:

    print(
        "GEMINI: SKIPPED "
        "(missing API key or SDK)"
    )


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


if GROQ_API_KEY:

    print(
        "GROQ CLIENT: READY"
    )

    print(
        "GROQ TEXT MODEL:",
        GROQ_MODEL
    )

    print(
        "GROQ VISION MODEL:",
        GROQ_VISION_MODEL
    )

else:

    print(
        "GROQ_API_KEY: NOT FOUND"
    )


# ============================================================
# GROQ SYSTEM PROMPT
# ============================================================

GROQ_SYSTEM_PROMPT = """
أنت Groq، العقل الأساسي في Ido AI.

أنت المسؤول الأول عن فهم طلب المستخدم والإجابة عليه.

القواعد:

1. أجب عن الأسئلة النصية بشكل طبيعي.
2. إذا بدأت الرسالة بتحية مثل:
   السلام عليكم
   مرحبا
   أهلا
   سلام
   ثم احتوت على طلب حقيقي، لا تكتفِ بالتحية.
   افهم الطلب الموجود بعد التحية ونفذه.
3. إذا طلب المستخدم إنشاء صورة، لا تقل:
   لا أستطيع إنشاء الصور.
4. في طلبات الصور، لا تقدم وصفًا طويلًا بدل الصورة.
5. طلب الصورة سيتم تحويله إلى مولد الصور بعد أن تفهمه.
6. عندما تكون الرسالة طلب صورة، أعد وصفًا واضحًا ومناسبًا كموجه Image Prompt.
7. لا تقل للمستخدم إنك لا تستطيع إنشاء الصور.
8. كن مختصرًا وطبيعيًا.
"""


# ============================================================
# REMOVE GREETING FROM IMAGE REQUEST
# ============================================================

GREETING_PREFIXES = [

    "السلام عليكم",
    "السلام عليكم ورحمة الله وبركاته",
    "سلام عليكم",

    "مرحبا",
    "مرحبًا",

    "اهلا",
    "أهلا",
    "أهلاً",

    "سلام",

    "hello",
    "hi",
    "hey"
]


def remove_greeting(
    message
):

    if not message:
        return ""

    text = str(
        message
    ).strip()

    lower = text.lower()

    changed = True

    while changed:

        changed = False

        for greeting in GREETING_PREFIXES:

            prefix = greeting.lower()

            if lower.startswith(prefix):

                text = text[
                    len(greeting):
                ].strip()

                # Remove punctuation after greeting.

                text = text.lstrip(
                    "،,.:;!؟? "
                )

                lower = text.lower()

                changed = True

                break

    return text.strip()


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_WORDS = [

    # Arabic

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

    "صور لي",
    "صورة لي",

    # English

    "generate an image",
    "generate image",

    "create an image",
    "create image",

    "make an image",
    "make image",

    "draw an image",
    "draw image",

    "create a picture",
    "generate a picture",

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

    # Remove greetings before detection.

    text_without_greeting = (
        remove_greeting(
            text
        )
    )

    return any(
        word.lower()
        in text_without_greeting
        for word in IMAGE_WORDS
    )


# ============================================================
# EXTRACT IMAGE PROMPT
# ============================================================

IMAGE_PREFIXES = [

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

    "صور لي",
    "صورة لي",

    "generate an image of",
    "generate image of",

    "create an image of",
    "create image of",

    "make an image of",
    "make image of",

    "draw an image of",

    "create a picture of",
    "generate a picture of",

    "make a picture of"
]


def get_image_prompt(
    message
):

    if not message:
        return ""

    text = remove_greeting(
        message
    )

    if not text:
        return ""

    lower = text.lower()

    for prefix in IMAGE_PREFIXES:

        prefix_lower = (
            prefix.lower()
        )

        if lower.startswith(
            prefix_lower
        ):

            return text[
                len(prefix):
            ].strip()

    return text


# ============================================================
# GROQ TEXT
# ============================================================

def ask_groq(
    message
):

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
                            "system",

                        "content":
                            GROQ_SYSTEM_PROMPT
                    },

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
            "Groq ERROR: timeout."
        )

        return None


    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: connection failed."
        )

        return None


    except Exception as exc:

        print(
            "Groq ERROR:",
            exc
        )

        return None


# ============================================================
# GEMINI TEXT
# ============================================================

def ask_gemini(
    message
):

    if not GEMINI_ENABLED:
        return None

    if gemini_client is None:
        return None

    if not message:
        return None

    if not provider_available(
        "GEMINI"
    ):
        return None

    try:

        print(
            "Trying Gemini TEXT..."
        )

        response = (
            gemini_client.models.generate_content(
                model=GEMINI_TEXT_MODEL,
                contents=message
            )
        )

        answer = clean_answer(
            getattr(
                response,
                "text",
                None
            )
        )

        if answer:

            print(
                "Gemini TEXT response received."
            )

            return answer

        return None


    except Exception as exc:

        text = str(
            exc
        )

        print(
            "Gemini TEXT ERROR:",
            text
        )


        if (
            "429" in text
            or
            "RESOURCE_EXHAUSTED"
            in text
        ):

            disable_provider(
                "GEMINI",
                "quota exceeded"
            )


        return None


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def generate_image_gemini(
    prompt
):

    if not GEMINI_ENABLED:

        print(
            "GEMINI IMAGE: "
            "CLIENT NOT AVAILABLE"
        )

        return None


    if gemini_client is None:

        return None


    if not prompt:

        return None


    if not provider_available(
        "GEMINI_IMAGE"
    ):

        print(
            "GEMINI IMAGE: "
            "TEMPORARILY DISABLED"
        )

        return None


    try:

        print(
            "=" * 60
        )

        print(
            "GEMINI IMAGE GENERATION STARTED"
        )

        print(
            "MODEL:",
            GEMINI_IMAGE_MODEL
        )

        print(
            "PROMPT:",
            prompt
        )

        print(
            "=" * 60
        )


        response = (
            gemini_client.models.generate_content(

                model=
                    GEMINI_IMAGE_MODEL,

                contents=
                    prompt,

                config=
                    types.GenerateContentConfig(

                        response_modalities=[
                            "IMAGE"
                        ]

                    )
            )
        )


        # ----------------------------------------------------
        # Find generated image
        # ----------------------------------------------------

        if not getattr(
            response,
            "candidates",
            None
        ):

            print(
                "GEMINI IMAGE: "
                "NO CANDIDATES"
            )

            return None


        for candidate in response.candidates:

            content = getattr(
                candidate,
                "content",
                None
            )


            if not content:
                continue


            parts = getattr(
                content,
                "parts",
                []
            )


            for part in parts:

                inline_data = getattr(
                    part,
                    "inline_data",
                    None
                )


                if not inline_data:
                    continue


                image_data = getattr(
                    inline_data,
                    "data",
                    None
                )


                mime_type = getattr(
                    inline_data,
                    "mime_type",
                    None
                )


                if not image_data:

                    continue


                if not mime_type:

                    mime_type = (
                        "image/png"
                    )


                # Google SDK can return bytes
                # directly.

                if isinstance(
                    image_data,
                    bytes
                ):

                    encoded = (
                        base64.b64encode(
                            image_data
                        ).decode(
                            "utf-8"
                        )
                    )

                else:

                    encoded = str(
                        image_data
                    )


                image_url = (
                    f"data:{mime_type};base64,"
                    f"{encoded}"
                )


                print(
                    "GEMINI IMAGE: SUCCESS"
                )


                return image_url


        print(
            "GEMINI IMAGE: "
            "NO IMAGE DATA FOUND"
        )


        # Helpful debug.

        try:

            print(
                "GEMINI RESPONSE:",
                response
            )

        except Exception:
            pass


        return None


    except Exception as exc:

        text = str(
            exc
        )


        print(
            "GEMINI IMAGE ERROR:",
            text
        )


        if (
            "429" in text
            or
            "RESOURCE_EXHAUSTED"
            in text
        ):

            disable_provider(
                "GEMINI_IMAGE",
                "quota exceeded"
            )


        return None


# ============================================================
# PRIMARY IMAGE ROUTER
# ============================================================

def generate_image(
    prompt
):

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


    print(
        "=" * 60
    )

    print(
        "IMAGE REQUEST DETECTED"
    )

    print(
        "PRIMARY UNDERSTANDING AI: GROQ"
    )

    print(
        "IMAGE ENGINE: GEMINI"
    )

    print(
        "IMAGE PROMPT:",
        prompt
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Groq does NOT get asked to generate the actual image.
    #
    # Groq's role is understanding.
    #
    # Gemini is the actual image engine.
    # --------------------------------------------------------


    # --------------------------------------------------------
    # GEMINI IMAGE
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


    # --------------------------------------------------------
    # FAILED
    # --------------------------------------------------------

    print(
        "GEMINI IMAGE FAILED."
    )


    return {

        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تحقق من GEMINI_API_KEY "
            "وحصة Gemini.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# QUICK RESPONSES
# ============================================================

#
# IMPORTANT:
#
# We intentionally DO NOT use substring matching here.
#
# The old system caused:
#
# "السلام عليكم، أنشئ لي صورة..."
#
# to match "سلام" and return a saved greeting.
#
# That behavior is removed.
# ============================================================

QUICK_RESPONSES = {

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

    "من برمجك":
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI.",

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


    #
    # IMPORTANT:
    #
    # Exact matching only.
    #
    # We no longer do:
    #
    # if "سلام" in text
    #
    # because that breaks:
    #
    # "السلام عليكم، أنشئ لي صورة..."
    #


    for key, value in (
        QUICK_RESPONSES.items()
    ):

        if text == key.lower():

            return value


    return None


# ============================================================
# MAIN RESPONSE ROUTER
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    if not message:

        return (
            "اكتب رسالة أولًا."
        )


    original_message = str(
        message
    ).strip()


    if not original_message:

        return (
            "اكتب رسالة أولًا."
        )


    # ========================================================
    # IMAGE REQUEST MUST BE CHECKED FIRST
    # ========================================================
    #
    # This is the most important fix.
    #
    # We do NOT send an image request to Groq as normal text.
    #
    # Otherwise Groq can answer:
    #
    # "I cannot create images..."
    #
    # ========================================================

    if is_image_generation_request(
        original_message
    ):

        prompt = get_image_prompt(
            original_message
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

        return quick


    # ========================================================
    # TEXT ROUTE
    # ========================================================
    #
    # PRIMARY:
    #     GROQ
    #
    # SECONDARY:
    #     MISTRAL
    #     OPENROUTER
    #     GEMINI
    #     XAI
    #     POLLINATIONS
    #
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
            "GEMINI",
            ask_gemini
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


    return (
        "أنا Ido AI، لكن جميع مزودي الذكاء "
        "الاصطناعي المتاحين فشلوا حاليًا. "
        "تحقق من المفاتيح والرصيد."
    )


# ============================================================
# MISTRAL - TEXT
# ============================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)


MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest"
)


MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "pixtral-12b-2409"
)


if MISTRAL_API_KEY:

    print(
        "MISTRAL CLIENT: READY"
    )

    print(
        "MISTRAL MODEL:",
        MISTRAL_MODEL
    )

    print(
        "MISTRAL VISION MODEL:",
        MISTRAL_VISION_MODEL
    )

else:

    print(
        "MISTRAL_API_KEY: NOT FOUND"
    )


def ask_mistral(
    message
):

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


        answer = clean_answer(
            content
        )


        if answer:

            print(
                "Mistral response received."
            )

            return answer


        return None


    except Exception as exc:

        print(
            "Mistral ERROR:",
            exc
        )

        return None


# ============================================================
# OPENROUTER - TEXT
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
)


OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)


if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
    )

else:

    print(
        "OPENROUTER_API_KEY: NOT FOUND"
    )


def openrouter_headers():

    return {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "X-Title":
            "Ido AI"
    }


def ask_openrouter(
    message
):

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

            headers=
                openrouter_headers(),

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
# XAI - TEXT ONLY
# ============================================================

XAI_API_KEY = os.getenv(
    "XAI_API_KEY"
)


XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)


XAI_MODEL = os.getenv(
    "XAI_MODEL",
    "grok-4.5"
)


if XAI_API_KEY:

    print(
        "XAI CLIENT: READY"
    )

else:

    print(
        "XAI_API_KEY: NOT FOUND"
    )


def ask_xai(
    message
):

    if not XAI_API_KEY:

        return None


    if not message:

        return None


    if not provider_available(
        "XAI"
    ):

        return None


    try:

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


        if response.status_code != 200:

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
# POLLINATIONS - TEXT ONLY
# ============================================================

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)


POLLINATIONS_CHAT_URL = (
    "https://gen.pollinations.ai/v1/chat/completions"
)


POLLINATIONS_TEXT_MODEL = os.getenv(
    "POLLINATIONS_TEXT_MODEL",
    "openai"
)


if POLLINATIONS_API_KEY:

    print(
        "POLLINATIONS CLIENT: READY"
    )

else:

    print(
        "POLLINATIONS_API_KEY: NOT FOUND"
    )


def ask_pollinations(
    message
):

    if not POLLINATIONS_API_KEY:

        return None


    if not message:

        return None


    if not provider_available(
        "POLLINATIONS"
    ):

        return None


    try:

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


        if response.status_code != 200:

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
                            "system",

                        "content":
                            GROQ_SYSTEM_PROMPT
                    },

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
                "Groq Vision response received."
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
# GEMINI VISION / IMAGE EDITING
# ============================================================

def ask_gemini_image(
    message,
    image_bytes,
    mime_type
):

    if not GEMINI_ENABLED:

        return None


    if gemini_client is None:

        return None


    if not image_bytes:

        return None


    if not provider_available(
        "GEMINI_VISION"
    ):

        return None


    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )


        response = (
            gemini_client.models.generate_content(

                model=
                    GEMINI_IMAGE_MODEL,

                contents=[

                    types.Part.from_text(
                        text=message
                    ),

                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )

                ],

                config=
                    types.GenerateContentConfig(

                        response_modalities=[
                            "IMAGE"
                        ]

                    )
            )
        )


        if not getattr(
            response,
            "candidates",
            None
        ):

            return None


        for candidate in response.candidates:

            content = getattr(
                candidate,
                "content",
                None
            )


            if not content:

                continue


            parts = getattr(
                content,
                "parts",
                []
            )


            for part in parts:

                inline_data = getattr(
                    part,
                    "inline_data",
                    None
                )


                if not inline_data:

                    continue


                data = getattr(
                    inline_data,
                    "data",
                    None
                )


                if not data:

                    continue


                result_mime = getattr(
                    inline_data,
                    "mime_type",
                    None
                )


                if not result_mime:

                    result_mime = (
                        "image/png"
                    )


                if isinstance(
                    data,
                    bytes
                ):

                    encoded_result = (
                        base64.b64encode(
                            data
                        ).decode(
                            "utf-8"
                        )
                    )

                else:

                    encoded_result = str(
                        data
                    )


                return (
                    f"data:{result_mime};base64,"
                    f"{encoded_result}"
                )


        return None


    except Exception as exc:

        print(
            "Gemini Vision ERROR:",
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


    if not message or not str(
        message
    ).strip():

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )


    message = str(
        message
    ).strip()


    # ========================================================
    # IMAGE EDIT / IMAGE GENERATION WITH INPUT IMAGE
    # ========================================================
    #
    # Gemini is the actual image engine here.
    #
    # ========================================================

    edited_image = ask_gemini_image(

        message,

        image_bytes,

        mime_type
    )


    if edited_image:

        print(
            "IMAGE ROUTE SUCCESS: GEMINI"
        )


        return {

            "answer":
                "تم إنشاء/تعديل الصورة بنجاح بواسطة Gemini.",

            "imageUrl":
                edited_image,

            "provider":
                "Gemini"
        }


    # ========================================================
    # IMAGE UNDERSTANDING
    # ========================================================
    #
    # If Gemini image processing is unavailable,
    # use Groq Vision for analysis.
    #
    # ========================================================

    answer = ask_groq_image(

        message,

        image_bytes,

        mime_type
    )


    if answer:

        print(
            "VISION ROUTE SUCCESS: GROQ"
        )

        return answer


    return (
        "تعذر تحليل الصورة حاليًا. "
        "تحقق من مفاتيح Groq وGemini."
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


# ============================================================
# STARTUP LOG
# ============================================================

print(
    "=" * 60
)

print(
    "IDO AI BRAIN.PY LOADED"
)

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
    "    GROQ -> MISTRAL -> OPENROUTER "
    "-> GEMINI -> XAI -> POLLINATIONS"
)

print(
    "IMAGE UNDERSTANDING:"
)

print(
    "    GROQ VISION"
)

print(
    "IMAGE GENERATION:"
)

print(
    "    GEMINI 3.1 FLASH IMAGE"
)

print(
    "GREETING:"
)

print(
    "    EXACT MATCH ONLY"
)

print(
    "IMAGE REQUEST:"
)

print(
    "    DETECT BEFORE TEXT ROUTE"
)

print(
    "=" * 60
)