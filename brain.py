# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL PROVIDER ROUTING
#
# TEXT:
#     XAI
#       ↓
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# IMAGE UNDERSTANDING:
#     XAI VISION
#       ↓
#     MISTRAL VISION
#       ↓
#     GROQ VISION
#
# IMAGE GENERATION:
#     XAI IMAGE
#       ↓
#     MISTRAL IMAGE
#
# IMAGE EDITING:
#     XAI IMAGE EDIT
#       ↓
#     MISTRAL VISION + IMAGE
#
# IMPORTANT:
#     Groq does NOT provide an image-generation endpoint.
#     Therefore Groq is used as an image-understanding
#     fallback, while Mistral is the image-generation fallback.
#
# ============================================================

import os
import re
import base64
import time
import random
import requests

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)


# ============================================================
# API KEYS
# ============================================================

XAI_API_KEY = os.getenv(
    "XAI_API_KEY",
    ""
).strip()


MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
).strip()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# ============================================================
# TEXT MODELS
# ============================================================

XAI_TEXT_MODEL = os.getenv(
    "XAI_TEXT_MODEL",
    "grok-4.5"
).strip()


GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash"
).strip()


# ============================================================
# VISION MODELS
# ============================================================

XAI_VISION_MODEL = os.getenv(
    "XAI_VISION_MODEL",
    "grok-4.5"
).strip()


MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
).strip()


# Optional Groq vision model.
#
# If this variable is not present, Groq vision is disabled.
#

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    ""
).strip()


# ============================================================
# IMAGE MODELS
# ============================================================

XAI_IMAGE_MODEL = os.getenv(
    "XAI_IMAGE_MODEL",
    "grok-imagine-image-quality"
).strip()


MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
).strip()


# ============================================================
# API URLS
# ============================================================

XAI_BASE_URL = (
    "https://api.x.ai/v1"
)


XAI_CHAT_URL = (
    f"{XAI_BASE_URL}/chat/completions"
)


XAI_RESPONSES_URL = (
    f"{XAI_BASE_URL}/responses"
)


XAI_IMAGE_GENERATION_URL = (
    f"{XAI_BASE_URL}/images/generations"
)


XAI_IMAGE_EDIT_URL = (
    f"{XAI_BASE_URL}/images/edits"
)


GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
)


MISTRAL_CHAT_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


MISTRAL_FILES_URL = (
    "https://api.mistral.ai/v1/files"
)


# ============================================================
# REQUEST TIMEOUT
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv(
        "AI_REQUEST_TIMEOUT",
        "180"
    )
)


# ============================================================
# MISTRAL RETRY SETTINGS
# ============================================================

MISTRAL_MAX_RETRIES = int(
    os.getenv(
        "MISTRAL_MAX_RETRIES",
        "2"
    )
)


MISTRAL_RETRY_BASE_SECONDS = float(
    os.getenv(
        "MISTRAL_RETRY_BASE_SECONDS",
        "2"
    )
)


MISTRAL_RETRY_MAX_SECONDS = float(
    os.getenv(
        "MISTRAL_RETRY_MAX_SECONDS",
        "30"
    )
)


MISTRAL_RETRY_JITTER = float(
    os.getenv(
        "MISTRAL_RETRY_JITTER",
        "0.5"
    )
)


if MISTRAL_MAX_RETRIES < 0:
    MISTRAL_MAX_RETRIES = 0


if MISTRAL_RETRY_BASE_SECONDS < 0:
    MISTRAL_RETRY_BASE_SECONDS = 0


if MISTRAL_RETRY_MAX_SECONDS < 0:
    MISTRAL_RETRY_MAX_SECONDS = 30


if MISTRAL_RETRY_JITTER < 0:
    MISTRAL_RETRY_JITTER = 0


# ============================================================
# CLIENT STATUS
# ============================================================

print(
    "XAI CLIENT:",
    "READY" if XAI_API_KEY else "MISSING"
)

print(
    "MISTRAL CLIENT:",
    "READY" if MISTRAL_API_KEY else "MISSING"
)

print(
    "GROQ CLIENT:",
    "READY" if GROQ_API_KEY else "MISSING"
)

print(
    "OPENROUTER CLIENT:",
    "READY" if OPENROUTER_API_KEY else "MISSING"
)

print(
    "GEMINI CLIENT:",
    "READY" if GEMINI_API_KEY else "MISSING"
)

print("=" * 70)

print(
    "XAI TEXT MODEL:",
    XAI_TEXT_MODEL
)

print(
    "XAI VISION MODEL:",
    XAI_VISION_MODEL
)

print(
    "XAI IMAGE MODEL:",
    XAI_IMAGE_MODEL
)

print(
    "MISTRAL VISION MODEL:",
    MISTRAL_VISION_MODEL
)

print(
    "MISTRAL IMAGE MODEL:",
    MISTRAL_IMAGE_MODEL
)

print(
    "GROQ TEXT MODEL:",
    GROQ_TEXT_MODEL
)

print(
    "GROQ VISION MODEL:",
    GROQ_VISION_MODEL
        if GROQ_VISION_MODEL
        else "DISABLED"
)

print(
    "OPENROUTER TEXT MODEL:",
    OPENROUTER_TEXT_MODEL
)

print(
    "GEMINI TEXT MODEL:",
    GEMINI_TEXT_MODEL
)

print("=" * 70)

print(
    "MISTRAL MAX RETRIES:",
    MISTRAL_MAX_RETRIES
)

print(
    "MISTRAL RETRY BASE SECONDS:",
    MISTRAL_RETRY_BASE_SECONDS
)

print(
    "AI REQUEST TIMEOUT:",
    REQUEST_TIMEOUT
)

print("=" * 70)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Aido AI.

You are the primary AI assistant of the application.

RULES:

1. Answer naturally and directly.

2. Understand Arabic, English and French.

3. Answer in the language used by the user whenever possible.

4. If the user says:
   "السلام عليكم"

   and also asks a question,
   answer the question normally.

5. If the user only says:
   "السلام عليكم"

   respond:

   "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك؟"

6. Never claim that an image was generated unless
   the image service actually returned an image.

7. Image generation and editing are handled by the
   application's image system.

8. Never invent an image URL.

9. Never expose API keys.

10. Never mention internal provider routing unless
    the user explicitly asks about it.

11. Be concise for simple questions.

12. Be detailed when the user asks for an explanation.

13. Help with programming, mathematics, translation,
    general questions, explanations and normal text tasks.

14. If the user asks to create an image, the application
    image system must handle the image request.
"""


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_ONLY_PATTERNS = [

    r"^\s*السلام عليكم\s*[.!؟،]*\s*$",

    r"^\s*السلام عليكم ورحمة الله وبركاته\s*[.!؟،]*\s*$",

    r"^\s*السلام عليكم ورحمه الله وبركاته\s*[.!؟،]*\s*$",

    r"^\s*السلام عليكم ورحمه الله\s*[.!؟،]*\s*$",

    r"^\s*سلام عليكم\s*[.!؟،]*\s*$",
]


def is_greeting_only(message):

    if not message:
        return False

    text = str(message).strip()

    for pattern in GREETING_ONLY_PATTERNS:

        if re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

    return False


def greeting_response():

    return (
        "وعليكم السلام ورحمة الله وبركاته، "
        "كيف يمكنني مساعدتك؟"
    )


# ============================================================
# IMAGE GENERATION KEYWORDS
# ============================================================

IMAGE_GENERATION_KEYWORDS_AR = [

    "أنشئ صورة",
    "انشئ صورة",
    "أنشئ لي صورة",
    "انشئ لي صورة",

    "أنشئ صوره",
    "انشئ صوره",
    "أنشئ لي صوره",
    "انشئ لي صوره",

    "اصنع صورة",
    "اصنع صوره",
    "اصنع لي صورة",
    "اصنع لي صوره",

    "اعمل صورة",
    "اعمل صوره",
    "اعمل لي صورة",
    "اعمل لي صوره",

    "ولّد صورة",
    "ولد صورة",
    "ولّد صوره",
    "ولد صوره",

    "ولّد لي صورة",
    "ولد لي صورة",
    "ولّد لي صوره",
    "ولد لي صوره",

    "توليد صورة",
    "توليد صوره",

    "إنشاء صورة",
    "انشاء صورة",
    "إنشاء صوره",
    "انشاء صوره",

    "ارسم صورة",
    "ارسم صوره",
    "ارسم لي صورة",
    "ارسم لي صوره",

    "ارسم",
    "ارسم لي",

    "صمم صورة",
    "صمّم صورة",
    "صمم صوره",
    "صمّم صوره",

    "صمم لي صورة",
    "صمّم لي صورة",
    "صمم لي صوره",
    "صمّم لي صوره",

    "تصميم صورة",
    "تصميم صوره",

    "أعطني صورة",
    "اعطني صورة",
    "أعطني صوره",
    "اعطني صوره",

    "أعطني صورة ل",
    "اعطني صورة ل",
    "أعطني صوره ل",
    "اعطني صوره ل",

    "أعطني صورة عن",
    "اعطني صورة عن",
    "أعطني صوره عن",
    "اعطني صوره عن",

    "هل يمكنك إنشاء صورة",
    "هل يمكنك انشاء صورة",

    "هل يمكنك إنشاء صوره",
    "هل يمكنك انشاء صوره",

    "هل يمكنك رسم صورة",
    "هل يمكنك رسم صوره",

    "هل تستطيع إنشاء صورة",
    "هل تستطيع انشاء صورة",

    "هل تستطيع رسم صورة",
    "هل تستطيع رسم صوره",

    "صورة ل",
    "صوره ل",

    "صورة عن",
    "صوره عن",

    "رسمة ل",
    "رسمة عن",

    "رسمة جميلة ل",
    "رسمة جميلة عن",
]


IMAGE_GENERATION_KEYWORDS_EN = [

    "generate an image",
    "generate image",

    "create an image",
    "create image",

    "make an image",
    "make image",

    "draw an image",
    "draw image",

    "draw a picture",
    "draw picture",

    "generate a picture",
    "create a picture",

    "generate a photo",
    "create a photo",

    "make a picture",
    "make a photo",

    "give me an image",
    "give me a picture",
    "give me a photo",

    "can you generate an image",
    "can you create an image",

    "can you make an image",
    "can you draw an image",

    "an image of",
    "a picture of",
    "a photo of",

    "image of",
    "picture of",
    "photo of",
]


IMAGE_GENERATION_KEYWORDS_FR = [

    "génère une image",
    "genere une image",

    "générer une image",
    "generer une image",

    "crée une image",
    "cree une image",

    "créer une image",
    "creer une image",

    "faire une image",

    "dessine une image",
    "dessine-moi une image",

    "donne-moi une image",
    "donne moi une image",

    "une image de",
    "une photo de",

    "image de",
    "photo de",

    "peux-tu générer une image",
    "peux tu generer une image",

    "peux-tu créer une image",
    "peux tu creer une image",
]


# ============================================================
# IMAGE ANALYSIS KEYWORDS
# ============================================================

IMAGE_ANALYSIS_KEYWORDS_AR = [

    "حلل الصورة",
    "حلل الصوره",

    "حلل هذه الصورة",
    "حلل هذه الصوره",

    "حلل لي الصورة",
    "حلل لي الصوره",

    "تحليل الصورة",
    "تحليل الصوره",

    "تحليل هذه الصورة",
    "تحليل هذه الصوره",

    "ماذا في الصورة",
    "ماذا في الصوره",

    "ماذا يظهر في الصورة",
    "ماذا يظهر في الصوره",

    "ماذا يوجد في الصورة",
    "ماذا يوجد في الصوره",

    "اشرح الصورة",
    "اشرح الصوره",

    "اشرح لي الصورة",
    "اشرح لي الصوره",

    "صف الصورة",
    "صف الصوره",

    "صف لي الصورة",
    "صف لي الصوره",

    "اقرأ الصورة",
    "اقرأ الصوره",

    "اقرأ لي الصورة",
    "اقرأ لي الصوره",

    "افحص الصورة",
    "افحص الصوره",

    "افحص لي الصورة",
    "افحص لي الصوره",

    "ما الموجود في الصورة",
    "ما الموجود في الصوره",

    "ما هذا في الصورة",
    "ما هذا في الصوره",

    "هل يمكنك تحليل الصورة",
    "هل يمكنك تحليل الصوره",

    "هل تستطيع تحليل الصورة",
    "هل تستطيع تحليل الصوره",

    "انظر إلى الصورة",
    "انظر الى الصورة",

    "انظر إلى الصوره",
    "انظر الى الصوره",
]


IMAGE_ANALYSIS_KEYWORDS_EN = [

    "analyze the image",
    "analyze this image",

    "analyse the image",
    "analyse this image",

    "analyze image",
    "analyse image",

    "what is in the image",
    "what's in the image",

    "what does the image show",
    "what is shown in the image",

    "describe the image",
    "describe this image",

    "explain the image",
    "explain this image",

    "read the image",

    "look at the image",
    "look at this image",

    "can you analyze the image",
    "can you analyze this image",

    "can you describe the image",
    "can you describe this image",
]


IMAGE_ANALYSIS_KEYWORDS_FR = [

    "analyse l'image",
    "analyse cette image",

    "analyser l'image",
    "analyser cette image",

    "décris l'image",
    "décris cette image",

    "decris l'image",
    "decris cette image",

    "qu'est-ce qu'il y a dans l'image",

    "que montre l'image",

    "explique l'image",
    "explique cette image",

    "regarde l'image",
    "regarde cette image",
]


# ============================================================
# IMAGE EDIT KEYWORDS
# ============================================================

IMAGE_EDIT_KEYWORDS = [

    "عدل",
    "عدّل",
    "تعديل",

    "حرر",
    "حرّر",
    "تحرير",

    "غيّر",
    "غير",

    "أضف",
    "اضف",

    "احذف",

    "استبدل",
    "استبدلها",

    "غيّرها",
    "غيرها",

    "عدلها",
    "عدّلها",

    "حررها",
    "حرّرها",

    "edit",
    "modify",
    "change",

    "remove",
    "add",
    "replace",

    "modifier",
    "modifie",
    "changer",

    "supprimer",
    "ajouter",
    "remplacer",
]


# ============================================================
# KEYWORD HELPER
# ============================================================

def contains_any_keyword(
    text,
    keywords
):

    text = str(
        text or ""
    ).lower()

    for keyword in keywords:

        if keyword.lower() in text:

            return True

    return False


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

def is_image_generation_request(message):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    return (

        contains_any_keyword(
            text,
            IMAGE_GENERATION_KEYWORDS_AR
        )

        or

        contains_any_keyword(
            text,
            IMAGE_GENERATION_KEYWORDS_EN
        )

        or

        contains_any_keyword(
            text,
            IMAGE_GENERATION_KEYWORDS_FR
        )
    )


def is_image_analysis_request(message):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    return (

        contains_any_keyword(
            text,
            IMAGE_ANALYSIS_KEYWORDS_AR
        )

        or

        contains_any_keyword(
            text,
            IMAGE_ANALYSIS_KEYWORDS_EN
        )

        or

        contains_any_keyword(
            text,
            IMAGE_ANALYSIS_KEYWORDS_FR
        )
    )


def is_image_edit_request(message):

    if not message:
        return False

    return contains_any_keyword(
        str(message).strip().lower(),
        IMAGE_EDIT_KEYWORDS
    )


def is_image_request(message):

    return (
        is_image_generation_request(message)
        or
        is_image_analysis_request(message)
        or
        is_image_edit_request(message)
    )


# ============================================================
# CLEAN IMAGE PROMPT
# ============================================================

def clean_image_prompt(message):

    text = str(
        message or ""
    ).strip()


    if not text:

        return (
            "Create a high-quality professional image."
        )


    prefixes = [

        "أنشئ لي صورة",
        "انشئ لي صورة",
        "أنشئ صورة",
        "انشئ صورة",

        "أنشئ لي صوره",
        "انشئ لي صوره",
        "أنشئ صوره",
        "انشئ صوره",

        "أنشئ لي",
        "انشئ لي",
        "أنشئ",
        "انشئ",

        "اصنع لي صورة",
        "اصنع لي صوره",
        "اصنع صورة",
        "اصنع صوره",

        "اصنع لي",
        "اصنع",

        "اعمل لي صورة",
        "اعمل لي صوره",
        "اعمل صورة",
        "اعمل صوره",

        "اعمل لي",
        "اعمل",

        "ولّد لي صورة",
        "ولد لي صورة",
        "ولّد لي صوره",
        "ولد لي صوره",

        "ولّد صورة",
        "ولد صورة",
        "ولّد صوره",
        "ولد صوره",

        "ولّد لي",
        "ولد لي",
        "ولّد",
        "ولد",

        "توليد صورة",
        "توليد صوره",

        "إنشاء صورة",
        "انشاء صورة",
        "إنشاء صوره",
        "انشاء صوره",

        "ارسم لي صورة",
        "ارسم لي صوره",
        "ارسم صورة",
        "ارسم صوره",

        "ارسم لي",
        "ارسم",

        "صمم لي صورة",
        "صمّم لي صورة",
        "صمم صورة",
        "صمّم صورة",

        "صمم لي صوره",
        "صمّم لي صوره",
        "صمم صوره",
        "صمّم صوره",

        "أعطني صورة",
        "اعطني صورة",
        "أعطني صوره",
        "اعطني صوره",

        "أعطني صورة ل",
        "اعطني صورة ل",
        "أعطني صوره ل",
        "اعطني صوره ل",

        "أعطني صورة عن",
        "اعطني صورة عن",
        "أعطني صوره عن",
        "اعطني صوره عن",

        "هل يمكنك إنشاء صورة",
        "هل يمكنك انشاء صورة",
        "هل يمكنك إنشاء صوره",
        "هل يمكنك انشاء صوره",

        "هل يمكنك رسم صورة",
        "هل يمكنك رسم صوره",

        "هل تستطيع إنشاء صورة",
        "هل تستطيع انشاء صورة",

        "هل تستطيع رسم صورة",
        "هل تستطيع رسم صوره",

        "generate an image",
        "generate image",
        "create an image",
        "create image",

        "make an image",
        "make image",

        "draw an image",
        "draw image",

        "draw a picture",
        "draw picture",

        "generate a picture",
        "create a picture",

        "generate a photo",
        "create a photo",

        "give me an image",
        "give me a picture",
        "give me a photo",

        "generate",
        "create",
        "make",
        "draw",
    ]


    cleaned = text


    for prefix in prefixes:

        if cleaned.lower().startswith(
            prefix.lower()
        ):

            cleaned = cleaned[
                len(prefix):
            ].strip()

            break


    greeting_prefixes = [

        "السلام عليكم ورحمة الله وبركاته",
        "السلام عليكم ورحمه الله وبركاته",
        "السلام عليكم ورحمه الله",
        "السلام عليكم",
        "سلام عليكم",
    ]


    for greeting in greeting_prefixes:

        if cleaned.startswith(
            greeting
        ):

            cleaned = cleaned[
                len(greeting):
            ].strip()

            break


    polite_prefixes = [

        "هل يمكنك",
        "هل تستطيع",

        "لو سمحت",
        "من فضلك",

        "please",
        "can you",
        "could you",
    ]


    for prefix in polite_prefixes:

        if cleaned.lower().startswith(
            prefix.lower()
        ):

            cleaned = cleaned[
                len(prefix):
            ].strip()

            break


    return cleaned or text


# ============================================================
# HTTP HELPERS
# ============================================================

def safe_post(
    url,
    headers=None,
    json_data=None,
    timeout=REQUEST_TIMEOUT,
    params=None
):

    return requests.post(

        url,

        headers=headers or {},

        json=json_data,

        params=params,

        timeout=timeout
    )


def safe_get(
    url,
    headers=None,
    timeout=REQUEST_TIMEOUT,
    params=None
):

    return requests.get(

        url,

        headers=headers or {},

        params=params,

        timeout=timeout
    )


# ============================================================
# RETRY-AFTER
# ============================================================

def get_retry_after_seconds(response):

    if response is None:
        return None


    value = response.headers.get(
        "Retry-After"
    )


    if value is None:
        return None


    try:

        seconds = float(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    if seconds < 0:
        seconds = 0


    return min(
        seconds,
        MISTRAL_RETRY_MAX_SECONDS
    )


# ============================================================
# MISTRAL POST WITH RETRY
# ============================================================

def mistral_post_with_retry(
    url,
    headers=None,
    json_data=None,
    timeout=REQUEST_TIMEOUT
):

    total_attempts = (
        MISTRAL_MAX_RETRIES + 1
    )


    last_response = None


    for attempt_index in range(
        total_attempts
    ):

        attempt_number = (
            attempt_index + 1
        )


        print("=" * 70)

        print(
            "MISTRAL REQUEST ATTEMPT:",
            f"{attempt_number}/{total_attempts}"
        )

        print("=" * 70)


        try:

            response = safe_post(

                url,

                headers=headers,

                json_data=json_data,

                timeout=timeout
            )


        except requests.RequestException as e:

            print(
                "MISTRAL REQUEST EXCEPTION:",
                repr(e)
            )

            raise


        last_response = response


        if response.status_code != 429:

            return response


        print(
            "MISTRAL RATE LIMIT HIT:",
            response.status_code
        )


        if attempt_index >= MISTRAL_MAX_RETRIES:

            print(
                "MISTRAL RETRIES EXHAUSTED"
            )

            return response


        retry_after = (
            get_retry_after_seconds(
                response
            )
        )


        exponential_delay = (

            MISTRAL_RETRY_BASE_SECONDS
            *
            (
                2 ** attempt_index
            )
        )


        exponential_delay = min(

            exponential_delay,

            MISTRAL_RETRY_MAX_SECONDS
        )


        jitter = (

            random.uniform(
                0,
                MISTRAL_RETRY_JITTER
            )

            if MISTRAL_RETRY_JITTER > 0

            else 0
        )


        calculated_delay = min(

            exponential_delay + jitter,

            MISTRAL_RETRY_MAX_SECONDS
        )


        wait_seconds = (

            retry_after
            if retry_after is not None
            else calculated_delay
        )


        print(
            "MISTRAL WAIT:",
            round(
                wait_seconds,
                2
            ),
            "seconds"
        )


        if wait_seconds > 0:

            time.sleep(
                wait_seconds
            )


    return last_response


# ============================================================
# CONTENT EXTRACTION
# ============================================================

def extract_content_text(content):

    if isinstance(
        content,
        str
    ):

        return content.strip()


    if not isinstance(
        content,
        list
    ):

        return ""


    parts = []


    for item in content:

        if not isinstance(
            item,
            dict
        ):

            continue


        text = item.get(
            "text"
        )


        if text:

            parts.append(
                str(text)
            )


    return "\n".join(
        parts
    ).strip()


def extract_text_response(data):

    if not isinstance(
        data,
        dict
    ):

        return ""


    choices = data.get(
        "choices"
    )


    if not isinstance(
        choices,
        list
    ) or not choices:

        return ""


    first = choices[0]


    if not isinstance(
        first,
        dict
    ):

        return ""


    message = first.get(
        "message"
    )


    if isinstance(
        message,
        dict
    ):

        answer = extract_content_text(
            message.get(
                "content"
            )
        )


        if answer:

            return answer


    return ""


# ============================================================
# XAI HEADERS
# ============================================================

def xai_headers():

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing."
        )


    return {

        "Authorization":
            f"Bearer {XAI_API_KEY}",

        "Content-Type":
            "application/json"
    }


# ============================================================
# MISTRAL HEADERS
# ============================================================

def mistral_headers():

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )


    return {

        "Authorization":
            f"Bearer {MISTRAL_API_KEY}",

        "Content-Type":
            "application/json"
    }


# ============================================================
# XAI TEXT
# ============================================================

def xai_text(message):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing."
        )


    payload = {

        "model":
            XAI_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    str(message)
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096
    }


    print("=" * 70)

    print(
        "XAI TEXT REQUEST"
    )

    print(
        "MODEL:",
        XAI_TEXT_MODEL
    )

    print("=" * 70)


    response = safe_post(

        XAI_CHAT_URL,

        headers=xai_headers(),

        json_data=payload
    )


    print(
        "XAI TEXT STATUS:",
        response.status_code
    )


    if response.status_code >= 400:

        print(
            "XAI TEXT ERROR:",
            response.text[:5000]
        )

        raise RuntimeError(
            "xAI HTTP "
            f"{response.status_code}: "
            f"{response.text[:3000]}"
        )


    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"xAI returned invalid JSON: {e}"
        )


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "xAI returned an empty response."
        )


    return answer


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text(message):

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )


    payload = {

        "model":
            GROQ_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    str(message)
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096
    }


    response = safe_post(

        GROQ_URL,

        headers={

            "Authorization":
                f"Bearer {GROQ_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Groq HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )


    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"Groq returned invalid JSON: {e}"
        )


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "Groq returned an empty response."
        )


    return answer


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_text(message):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing."
        )


    payload = {

        "model":
            OPENROUTER_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {
                "role":
                    "user",

                "content":
                    str(message)
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096
    }


    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            os.getenv(
                "OPENROUTER_SITE_URL",
                "https://ido-ai-production.up.railway.app"
            ),

        "X-Title":
            "IDO AI"
    }


    response = safe_post(

        OPENROUTER_URL,

        headers=headers,

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "OpenRouter HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )


    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"OpenRouter returned invalid JSON: {e}"
        )


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "OpenRouter returned an empty response."
        )


    return answer


# ============================================================
# GEMINI TEXT
# ============================================================

def gemini_text(message):

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )


    url = (

        f"{GEMINI_URL}/models/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
    )


    payload = {

        "system_instruction": {

            "parts": [

                {
                    "text":
                        SYSTEM_PROMPT
                }
            ]
        },

        "contents": [

            {

                "role":
                    "user",

                "parts": [

                    {
                        "text":
                            str(message)
                    }
                ]
            }
        ],

        "generationConfig": {

            "temperature":
                0.7,

            "maxOutputTokens":
                4096
        }
    }


    response = safe_post(

        url,

        headers={
            "Content-Type":
                "application/json"
        },

        json_data=payload,

        params={
            "key":
                GEMINI_API_KEY
        }
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Gemini HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )


    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"Gemini returned invalid JSON: {e}"
        )


    candidates = data.get(
        "candidates"
    )


    if not isinstance(
        candidates,
        list
    ) or not candidates:

        raise RuntimeError(
            "Gemini returned no candidates."
        )


    first = candidates[0]


    content = first.get(
        "content",
        {}
    )


    parts = content.get(
        "parts",
        []
    )


    result_parts = []


    for part in parts:

        if not isinstance(
            part,
            dict
        ):

            continue


        text = part.get(
            "text"
        )


        if text:

            result_parts.append(
                str(text)
            )


    answer = "\n".join(
        result_parts
    ).strip()


    if not answer:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    return answer


# ============================================================
# XAI VISION
# ============================================================

def xai_vision(
    message,
    image_bytes,
    mime_type
):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing."
        )


    if not image_bytes:

        raise RuntimeError(
            "No image data was supplied."
        )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or "image/jpeg"
    )


    image_data_url = (

        f"data:{safe_mime};base64,"
        f"{encoded}"
    )


    question = (

        str(message).strip()

        if message

        else

        "حلل هذه الصورة واشرح لي ما الذي يظهر فيها."
    )


    payload = {

        "model":
            XAI_VISION_MODEL,

        "messages": [

            {

                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {

                "role":
                    "user",

                "content": [

                    {

                        "type":
                            "text",

                        "text":
                            question
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
        ],

        "temperature":
            0.3,

        "max_tokens":
            4096
    }


    print("=" * 70)

    print(
        "XAI VISION REQUEST"
    )

    print(
        "MODEL:",
        XAI_VISION_MODEL
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes)
    )

    print("=" * 70)


    response = safe_post(

        XAI_CHAT_URL,

        headers=xai_headers(),

        json_data=payload
    )


    print(
        "XAI VISION STATUS:",
        response.status_code
    )


    if response.status_code >= 400:

        print(
            "XAI VISION ERROR:",
            response.text[:7000]
        )

        raise RuntimeError(
            "xAI Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:3500]}"
        )


    data = response.json()


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "xAI Vision returned an empty response."
        )


    print(
        "XAI VISION SUCCESS"
    )


    return answer


# ============================================================
# MISTRAL VISION
# ============================================================

def mistral_vision(
    message,
    image_bytes,
    mime_type
):

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )


    if not image_bytes:

        raise RuntimeError(
            "No image data was supplied."
        )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or "image/jpeg"
    )


    image_data_url = (

        f"data:{safe_mime};base64,"
        f"{encoded}"
    )


    question = (

        str(message).strip()

        if message

        else

        "حلل هذه الصورة واشرح لي ما الذي يظهر فيها."
    )


    payload = {

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
                            question
                    },

                    {

                        "type":
                            "image_url",

                        "image_url":
                            image_data_url
                    }
                ]
            }
        ],

        "temperature":
            0.3,

        "max_tokens":
            4096
    }


    response = mistral_post_with_retry(

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:3500]}"
        )


    data = response.json()


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "Mistral Vision returned an empty response."
        )


    return answer


# ============================================================
# GROQ VISION
# ============================================================

def groq_vision(
    message,
    image_bytes,
    mime_type
):

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )


    if not GROQ_VISION_MODEL:

        raise RuntimeError(
            "GROQ_VISION_MODEL is not configured."
        )


    if not image_bytes:

        raise RuntimeError(
            "No image data was supplied."
        )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or "image/jpeg"
    )


    image_data_url = (

        f"data:{safe_mime};base64,"
        f"{encoded}"
    )


    question = (

        str(message).strip()

        if message

        else

        "Analyze this image."
    )


    payload = {

        "model":
            GROQ_VISION_MODEL,

        "messages": [

            {

                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT
            },

            {

                "role":
                    "user",

                "content": [

                    {

                        "type":
                            "text",

                        "text":
                            question
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
        ],

        "temperature":
            0.3,

        "max_tokens":
            4096
    }


    response = safe_post(

        GROQ_URL,

        headers={

            "Authorization":
                f"Bearer {GROQ_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Groq Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:3500]}"
        )


    data = response.json()


    answer = extract_text_response(
        data
    )


    if not answer:

        raise RuntimeError(
            "Groq Vision returned an empty response."
        )


    return answer


# ============================================================
# XAI IMAGE RESPONSE EXTRACTION
# ============================================================

def extract_xai_image_url(data):

    if not isinstance(
        data,
        dict
    ):

        return None


    items = data.get(
        "data"
    )


    if not isinstance(
        items,
        list
    ) or not items:

        return None


    first = items[0]


    if not isinstance(
        first,
        dict
    ):

        return None


    url = first.get(
        "url"
    )


    if url:

        return str(
            url
        )


    b64_json = first.get(
        "b64_json"
    )


    if b64_json:

        return (
            "data:image/png;base64,"
            + str(b64_json)
        )


    file_output = first.get(
        "file_output"
    )


    if isinstance(
        file_output,
        dict
    ):

        public_url = file_output.get(
            "public_url"
        )


        if public_url:

            return str(
                public_url
            )


    return None


# ============================================================
# XAI IMAGE GENERATION
# ============================================================

def xai_generate_image(
    prompt
):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing."
        )


    clean_prompt = clean_image_prompt(
        prompt
    )


    payload = {

        "model":
            XAI_IMAGE_MODEL,

        "prompt":
            clean_prompt,

        "response_format":
            "url",

        "n":
            1
    }


    print("=" * 70)

    print(
        "XAI IMAGE GENERATION REQUEST"
    )

    print(
        "URL:",
        XAI_IMAGE_GENERATION_URL
    )

    print(
        "MODEL:",
        XAI_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        clean_prompt
    )

    print("=" * 70)


    try:

        response = requests.post(

            XAI_IMAGE_GENERATION_URL,

            headers=xai_headers(),

            json=payload,

            timeout=REQUEST_TIMEOUT
        )


    except requests.Timeout as e:

        print(
            "XAI IMAGE TIMEOUT:",
            repr(e)
        )

        raise RuntimeError(
            "xAI Image request timed out."
        )


    except requests.RequestException as e:

        print(
            "XAI IMAGE REQUEST ERROR:",
            repr(e)
        )

        raise RuntimeError(
            f"xAI Image request failed: {e}"
        )


    print(
        "XAI IMAGE HTTP STATUS:",
        response.status_code
    )


    print(
        "XAI IMAGE RAW RESPONSE:"
    )

    print(
        response.text[:12000]
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "xAI Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:5000]}"
        )


    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "xAI Image returned invalid JSON: "
            f"{e}"
        )


    image_url = extract_xai_image_url(
        data
    )


    if not image_url:

        raise RuntimeError(
            "xAI returned no usable image URL."
        )


    print("=" * 70)

    print(
        "XAI IMAGE SUCCESS"
    )

    print(
        "IMAGE URL:",
        str(image_url)[:500]
    )

    print("=" * 70)


    return {

        "image_url":
            image_url,

        "text":
            "تم إنشاء الصورة بنجاح.",

        "provider":
            "xAI",

        "model":
            XAI_IMAGE_MODEL
    }


# ============================================================
# XAI IMAGE EDIT
# ============================================================

def xai_edit_image(
    prompt,
    image_bytes,
    mime_type
):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing."
        )


    if not image_bytes:

        raise RuntimeError(
            "No source image was supplied."
        )


    clean_prompt = str(
        prompt or ""
    ).strip()


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or "image/jpeg"
    )


    image_data_url = (

        f"data:{safe_mime};base64,"
        f"{encoded}"
    )


    payload = {

        "model":
            XAI_IMAGE_MODEL,

        "prompt":
            clean_prompt,

        "image": {

            "url":
                image_data_url,

            "type":
                "image_url"
        }
    }


    print("=" * 70)

    print(
        "XAI IMAGE EDIT REQUEST"
    )

    print(
        "MODEL:",
        XAI_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        clean_prompt
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes)
    )

    print("=" * 70)


    try:

        response = requests.post(

            XAI_IMAGE_EDIT_URL,

            headers=xai_headers(),

            json=payload,

            timeout=REQUEST_TIMEOUT
        )


    except requests.Timeout:

        raise RuntimeError(
            "xAI Image Edit request timed out."
        )


    except requests.RequestException as e:

        raise RuntimeError(
            f"xAI Image Edit request failed: {e}"
        )


    print(
        "XAI IMAGE EDIT STATUS:",
        response.status_code
    )


    print(
        "XAI IMAGE EDIT RESPONSE:"
    )

    print(
        response.text[:12000]
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "xAI Image Edit HTTP "
            f"{response.status_code}: "
            f"{response.text[:5000]}"
        )


    data = response.json()


    image_url = extract_xai_image_url(
        data
    )


    if not image_url:

        raise RuntimeError(
            "xAI Image Edit returned no usable image URL."
        )


    print(
        "XAI IMAGE EDIT SUCCESS"
    )


    return {

        "image_url":
            image_url,

        "text":
            "تم تعديل الصورة بنجاح.",

        "provider":
            "xAI",

        "model":
            XAI_IMAGE_MODEL
    }


# ============================================================
# MISTRAL IMAGE REFERENCE EXTRACTION
# ============================================================

def extract_mistral_image_reference(data):

    if not isinstance(
        data,
        (dict, list)
    ):

        return None


    def walk(value):

        if isinstance(
            value,
            dict
        ):

            if value.get(
                "type"
            ) == "tool_file":

                file_id = value.get(
                    "file_id"
                )


                if file_id:

                    return {

                        "type":
                            "file_id",

                        "value":
                            str(file_id)
                    }


            file_id = value.get(
                "file_id"
            )


            if file_id:

                return {

                    "type":
                        "file_id",

                    "value":
                        str(file_id)
                }


            image_url = value.get(
                "image_url"
            )


            if isinstance(
                image_url,
                str
            ):

                if (

                    image_url.startswith(
                        "http://"
                    )

                    or

                    image_url.startswith(
                        "https://"
                    )

                ):

                    return {

                        "type":
                            "url",

                        "value":
                            image_url
                    }


            if isinstance(
                image_url,
                dict
            ):

                url = image_url.get(
                    "url"
                )


                if url:

                    return {

                        "type":
                            "url",

                        "value":
                            str(url)
                    }


            for key in (
                "url",
                "image"
            ):

                item = value.get(
                    key
                )


                if isinstance(
                    item,
                    str
                ):

                    if (

                        item.startswith(
                            "http://"
                        )

                        or

                        item.startswith(
                            "https://"
                        )

                    ):

                        return {

                            "type":
                                "url",

                            "value":
                                item
                        }


            for key in (
                "messages",
                "choices",
                "content",
                "outputs",
                "output",
                "response",
                "tool_calls"
            ):

                child = value.get(
                    key
                )


                if child is not None:

                    result = walk(
                        child
                    )


                    if result:

                        return result


            for child in value.values():

                result = walk(
                    child
                )


                if result:

                    return result


        elif isinstance(
            value,
            list
        ):

            for item in value:

                result = walk(
                    item
                )


                if result:

                    return result


        return None


    return walk(
        data
    )


# ============================================================
# MISTRAL SIGNED FILE URL
# ============================================================

def mistral_file_signed_url(
    file_id,
    expiry_hours=24
):

    if not file_id:

        return None


    safe_expiry = max(

        1,

        min(
            int(expiry_hours),
            168
        )
    )


    url = (

        f"{MISTRAL_FILES_URL}/"
        f"{file_id}/url"
    )


    response = mistral_get_with_retry(

        url,

        headers=mistral_headers(),

        params={
            "expiry":
                safe_expiry
        }
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral File URL HTTP "
            f"{response.status_code}: "
            f"{response.text[:3000]}"
        )


    data = response.json()


    signed_url = data.get(
        "url"
    )


    if not signed_url:

        raise RuntimeError(
            "Mistral did not return a signed image URL."
        )


    return str(
        signed_url
    )


# ============================================================
# MISTRAL GET WITH RETRY
# ============================================================

def mistral_get_with_retry(
    url,
    headers=None,
    timeout=REQUEST_TIMEOUT,
    params=None
):

    total_attempts = (
        MISTRAL_MAX_RETRIES + 1
    )


    last_response = None


    for attempt_index in range(
        total_attempts
    ):

        try:

            response = safe_get(

                url,

                headers=headers,

                timeout=timeout,

                params=params
            )


        except requests.RequestException as e:

            raise


        last_response = response


        if response.status_code != 429:

            return response


        if attempt_index >= MISTRAL_MAX_RETRIES:

            return response


        retry_after = (
            get_retry_after_seconds(
                response
            )
        )


        delay = min(

            MISTRAL_RETRY_BASE_SECONDS
            *
            (
                2 ** attempt_index
            ),

            MISTRAL_RETRY_MAX_SECONDS
        )


        jitter = random.uniform(
            0,
            MISTRAL_RETRY_JITTER
        )


        wait_seconds = (

            retry_after

            if retry_after is not None

            else

            min(
                delay + jitter,
                MISTRAL_RETRY_MAX_SECONDS
            )
        )


        print(
            "MISTRAL GET WAIT:",
            round(
                wait_seconds,
                2
            )
        )


        if wait_seconds > 0:

            time.sleep(
                wait_seconds
            )


    return last_response


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_generate_image(
    prompt
):

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )


    clean_prompt = clean_image_prompt(
        prompt
    )


    payload = {

        "model":
            MISTRAL_IMAGE_MODEL,

        "messages": [

            {

                "role":
                    "system",

                "content":
                    (
                        "You are Aido AI image generation "
                        "system. Use the image_generation "
                        "tool whenever an image is requested. "
                        "Return the generated image."
                    )
            },

            {

                "role":
                    "user",

                "content":
                    clean_prompt
            }
        ],

        "tools": [

            {

                "type":
                    "image_generation"
            }
        ],

        "tool_choice":
            "required"
    }


    print("=" * 70)

    print(
        "MISTRAL IMAGE GENERATION REQUEST"
    )

    print(
        "MODEL:",
        MISTRAL_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        clean_prompt
    )

    print("=" * 70)


    response = mistral_post_with_retry(

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload
    )


    print(
        "MISTRAL IMAGE STATUS:",
        response.status_code
    )


    print(
        "MISTRAL IMAGE RESPONSE:"
    )

    print(
        response.text[:12000]
    )


    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:5000]}"
        )


    data = response.json()


    reference = (
        extract_mistral_image_reference(
            data
        )
    )


    if not reference:

        text_answer = extract_text_response(
            data
        )


        if text_answer:

            raise RuntimeError(
                "Mistral returned text instead of "
                "an image: "
                f"{text_answer[:2500]}"
            )


        raise RuntimeError(
            "Mistral returned no generated image reference."
        )


    reference_type = reference.get(
        "type"
    )


    reference_value = reference.get(
        "value"
    )


    if reference_type == "url":

        image_url = str(
            reference_value
        )


    elif reference_type == "file_id":

        image_url = (
            mistral_file_signed_url(
                reference_value
            )
        )


    else:

        raise RuntimeError(
            "Unsupported Mistral image reference type."
        )


    if not image_url:

        raise RuntimeError(
            "Mistral returned no usable image URL."
        )


    print("=" * 70)

    print(
        "MISTRAL IMAGE SUCCESS"
    )

    print(
        "IMAGE URL:",
        str(image_url)[:500]
    )

    print("=" * 70)


    return {

        "image_url":
            image_url,

        "text":
            "تم إنشاء الصورة بنجاح.",

        "provider":
            "Mistral",

        "model":
            MISTRAL_IMAGE_MODEL
    }


# ============================================================
# MISTRAL IMAGE EDITING
# ============================================================

def mistral_edit_image(
    prompt,
    image_bytes,
    mime_type
):

    if not image_bytes:

        raise RuntimeError(
            "No source image was supplied."
        )


    print("=" * 70)

    print(
        "MISTRAL IMAGE EDIT REQUEST"
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 70)


    source_description = mistral_vision(

        (
            "Describe this image accurately so it can "
            "be recreated and modified. Include the "
            "main subject, composition, background, "
            "objects, colors, lighting, clothing, "
            "environment and style. Do not invent "
            "details that are not visible."
        ),

        image_bytes,

        mime_type
    )


    transformed_prompt = f"""
Create a final image based on the original image
description and the requested modification.

ORIGINAL IMAGE:
{source_description}

USER REQUEST:
{prompt}

Preserve the original subject, composition,
important visual characteristics and environment
unless the user explicitly asks to change them.

Apply the requested modification accurately.
Return the final visual result.
""".strip()


    result = mistral_generate_image(
        transformed_prompt
    )


    result["text"] = (
        "تم تعديل الصورة بنجاح."
    )


    return result


# ============================================================
# IMAGE GENERATION WITH FALLBACKS
# ============================================================

def generate_image_with_fallbacks(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

    prompt = clean_image_prompt(
        message
    )


    print("=" * 70)

    print(
        "IMAGE GENERATION START"
    )

    print(
        "PROMPT:",
        prompt
    )

    print(
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 70)


    # ========================================================
    # IMAGE EDIT
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # XAI EDIT
        # ----------------------------------------------------

        try:

            print(
                "TRYING IMAGE EDIT PROVIDER: xAI"
            )


            result = xai_edit_image(

                prompt,

                image_bytes,

                mime_type
            )


            if result.get(
                "image_url"
            ):

                return result


        except Exception as e:

            print(
                "xAI IMAGE EDIT FAILED:",
                repr(e)
            )


        # ----------------------------------------------------
        # MISTRAL EDIT FALLBACK
        # ----------------------------------------------------

        try:

            print(
                "TRYING IMAGE EDIT PROVIDER: Mistral"
            )


            result = mistral_edit_image(

                prompt,

                image_bytes,

                mime_type
            )


            if result.get(
                "image_url"
            ):

                return result


        except Exception as e:

            print(
                "MISTRAL IMAGE EDIT FAILED:",
                repr(e)
            )


        raise RuntimeError(
            "Both xAI and Mistral image editing failed."
        )


    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    # --------------------------------------------------------
    # PRIMARY: XAI
    # --------------------------------------------------------

    try:

        print(
            "TRYING IMAGE GENERATION PROVIDER: xAI"
        )


        result = xai_generate_image(
            prompt
        )


        if result.get(
            "image_url"
        ):

            return result


    except Exception as e:

        print("=" * 70)

        print(
            "XAI IMAGE GENERATION FAILED"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "ERROR REPR:",
            repr(e)
        )

        print("=" * 70)


    # --------------------------------------------------------
    # FALLBACK: MISTRAL
    # --------------------------------------------------------

    try:

        print(
            "TRYING IMAGE GENERATION PROVIDER: Mistral"
        )


        result = mistral_generate_image(
            prompt
        )


        if result.get(
            "image_url"
        ):

            return result


    except Exception as e:

        print("=" * 70)

        print(
            "MISTRAL IMAGE GENERATION FAILED"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "ERROR REPR:",
            repr(e)
        )

        print("=" * 70)


    raise RuntimeError(
        "xAI and Mistral image generation failed."
    )


# ============================================================
# GET IMAGE RESPONSE
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

    message = str(
        message or ""
    ).strip()


    print("=" * 70)

    print(
        "IMAGE REQUEST"
    )

    print(
        "MESSAGE:",
        message
    )

    print(
        "HAS INPUT IMAGE:",
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

    print("=" * 70)


    # ========================================================
    # UPLOADED IMAGE
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        if is_image_edit_request(
            message
        ):

            try:

                result = (
                    generate_image_with_fallbacks(

                        message,

                        image_bytes,

                        mime_type,

                        conversation_id
                    )
                )


                return {

                    "answer":
                        result.get(
                            "text",
                            "تم تعديل الصورة بنجاح."
                        ),

                    "imageUrl":
                        result.get(
                            "image_url",
                            ""
                        ),

                    "provider":
                        result.get(
                            "provider"
                        ),

                    "conversation_id":
                        conversation_id
                }


            except Exception as e:

                print(
                    "IMAGE EDIT FAILED:",
                    repr(e)
                )


                return {

                    "answer":
                        (
                            "تعذر تعديل الصورة حاليًا. "
                            "تمت تجربة xAI وMistral."
                        ),

                    "imageUrl":
                        "",

                    "provider":
                        None,

                    "conversation_id":
                        conversation_id
                }


        # ----------------------------------------------------
        # XAI VISION
        # ----------------------------------------------------

        try:

            print(
                "TRYING IMAGE UNDERSTANDING PROVIDER: xAI"
            )


            answer = xai_vision(

                message,

                image_bytes,

                mime_type
            )


            return {

                "answer":
                    answer,

                "imageUrl":
                    "",

                "provider":
                    "xAI Vision",

                "conversation_id":
                    conversation_id
            }


        except Exception as e:

            print(
                "XAI VISION FAILED:",
                repr(e)
            )


        # ----------------------------------------------------
        # MISTRAL VISION
        # ----------------------------------------------------

        try:

            print(
                "TRYING IMAGE UNDERSTANDING PROVIDER: Mistral"
            )


            answer = mistral_vision(

                message,

                image_bytes,

                mime_type
            )


            return {

                "answer":
                    answer,

                "imageUrl":
                    "",

                "provider":
                    "Mistral Vision",

                "conversation_id":
                    conversation_id
            }


        except Exception as e:

            print(
                "MISTRAL VISION FAILED:",
                repr(e)
            )


        # ----------------------------------------------------
        # GROQ VISION
        # ----------------------------------------------------

        if GROQ_VISION_MODEL:

            try:

                print(
                    "TRYING IMAGE UNDERSTANDING PROVIDER: Groq"
                )


                answer = groq_vision(

                    message,

                    image_bytes,

                    mime_type
                )


                return {

                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        "Groq Vision",

                    "conversation_id":
                        conversation_id
                }


            except Exception as e:

                print(
                    "GROQ VISION FAILED:",
                    repr(e)
                )


        return {

            "answer":
                (
                    "تعذر تحليل الصورة حاليًا "
                    "باستخدام خدمات الرؤية المتاحة."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # ANALYSIS WITHOUT IMAGE
    # ========================================================

    if is_image_analysis_request(
        message
    ):

        return {

            "answer":
                (
                    "أرسل الصورة أولًا، ثم سأقوم "
                    "بتحليلها لك."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # TEXT -> IMAGE
    # ========================================================

    try:

        result = generate_image_with_fallbacks(

            message,

            None,

            None,

            conversation_id
        )


        return {

            "answer":
                result.get(
                    "text",
                    "تم إنشاء الصورة بنجاح."
                ),

            "imageUrl":
                result.get(
                    "image_url",
                    ""
                ),

            "provider":
                result.get(
                    "provider"
                ),

            "conversation_id":
                conversation_id
        }


    except Exception as e:

        print("=" * 70)

        print(
            "ALL IMAGE GENERATION PROVIDERS FAILED"
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "ERROR REPR:",
            repr(e)
        )

        print("=" * 70)


        return {

            "answer":
                (
                    "تعذر إنشاء الصورة حاليًا. "
                    "تمت تجربة xAI وMistral."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }


# ============================================================
# GET RESPONSE
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    message = str(
        message or ""
    ).strip()


    if not message:

        return {

            "answer":
                "اكتب رسالة أولًا.",

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }


    print("=" * 70)

    print(
        "DYNAMIC AI RESPONSE"
    )

    print(
        "MESSAGE:",
        message
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 70)


    # ========================================================
    # GREETING
    # ========================================================

    if is_greeting_only(
        message
    ):

        return {

            "answer":
                greeting_response(),

            "imageUrl":
                "",

            "provider":
                "Aido AI",

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    if is_image_generation_request(
        message
    ):

        print(
            "IMAGE REQUEST DETECTED"
        )


        return get_image_response(

            message,

            None,

            None,

            conversation_id
        )


    # ========================================================
    # IMAGE ANALYSIS WITHOUT IMAGE
    # ========================================================

    if is_image_analysis_request(
        message
    ):

        return {

            "answer":
                (
                    "أرسل الصورة أولًا، ثم سأقوم "
                    "بتحليلها لك."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # TEXT PROVIDERS
    #
    # XAI IS PRIMARY
    # ========================================================

    providers = [

        (
            "xAI",
            xai_text
        ),

        (
            "Groq",
            groq_text
        ),

        (
            "OpenRouter",
            openrouter_text
        ),

        (
            "Gemini",
            gemini_text
        )
    ]


    errors = []


    for (
        provider_name,
        provider_function
    ) in providers:

        try:

            print(
                "TRYING TEXT PROVIDER:",
                provider_name
            )


            answer = provider_function(
                message
            )


            if answer:

                print(
                    "TEXT PROVIDER SUCCESS:",
                    provider_name
                )


                return {

                    "answer":
                        answer,

                    "imageUrl":
                        "",

                    "provider":
                        provider_name,

                    "conversation_id":
                        conversation_id
                }


        except Exception as e:

            error_text = (

                f"{provider_name}: "
                f"{e}"
            )


            errors.append(
                error_text
            )


            print(
                "TEXT PROVIDER FAILED:",
                error_text
            )


    # ========================================================
    # ALL TEXT PROVIDERS FAILED
    # ========================================================

    print(
        "ALL TEXT PROVIDERS FAILED"
    )


    for error in errors:

        print(
            "TEXT ERROR:",
            error
        )


    return {

        "answer":
            (
                "تعذر الحصول على إجابة "
                "من خدمات الذكاء الاصطناعي حاليًا."
            ),

        "imageUrl":
            "",

        "provider":
            None,

        "conversation_id":
            conversation_id
    }


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message
):

    return get_response(
        message
    )


# ============================================================
# ASK
# ============================================================

def ask(
    message,
    conversation_id=None
):

    return get_response(

        message,

        conversation_id=
            conversation_id
    )


# ============================================================
# COMPATIBILITY INFORMATION
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

print("=" * 70)


# ============================================================
# FINAL PROVIDER ROUTING
# ============================================================

print(
    "FINAL PROVIDER ROUTING"
)

print("-" * 70)

print(
    "TEXT:"
)

print(
    "    XAI"
)

print(
    "      ↓"
)

print(
    "    GROQ"
)

print(
    "      ↓"
)

print(
    "    OPENROUTER"
)

print(
    "      ↓"
)

print(
    "    GEMINI"
)

print("-" * 70)

print(
    "IMAGE UNDERSTANDING:"
)

print(
    "    XAI VISION"
)

print(
    "      ↓"
)

print(
    "    MISTRAL VISION"
)

print(
    "      ↓"
)

print(
    "    GROQ VISION"
)

print("-" * 70)

print(
    "IMAGE GENERATION:"
)

print(
    "    XAI IMAGE"
)

print(
    "      ↓"
)

print(
    "    MISTRAL IMAGE"
)

print("-" * 70)

print(
    "IMAGE EDITING:"
)

print(
    "    XAI IMAGE EDIT"
)

print(
    "      ↓"
)

print(
    "    MISTRAL VISION + IMAGE"
)

print("-" * 70)

print(
    "XAI:"
)

print(
    "    TEXT"
)

print(
    "    VISION"
)

print(
    "    IMAGE GENERATION"
)

print(
    "    IMAGE EDITING"
)

print("-" * 70)

print(
    "MISTRAL:"
)

print(
    "    VISION"
)

print(
    "    IMAGE GENERATION FALLBACK"
)

print(
    "    IMAGE EDITING FALLBACK"
)

print("-" * 70)

print(
    "GROQ:"
)

print(
    "    TEXT FALLBACK"
)

print(
    "    VISION FALLBACK"
)

print(
    "    IMAGE GENERATION:"
)

print(
    "        NOT AVAILABLE THROUGH GROQ API"
)

print("-" * 70)

print(
    "OPENROUTER:"
)

print(
    "    TEXT FALLBACK"
)

print("-" * 70)

print(
    "GEMINI:"
)

print(
    "    TEXT FALLBACK"
)

print("-" * 70)

print(
    "MISTRAL RATE LIMIT RETRY:"
)

print(
    "    ENABLED"
)

print(
    "    429 -> EXPONENTIAL BACKOFF"
)

print(
    "    RETRY-AFTER -> SUPPORTED"
)

print("-" * 70)

print(
    "xAI IMAGE ENDPOINT:"
)

print(
    "    /v1/images/generations"
)

print("-" * 70)

print(
    "xAI IMAGE EDIT ENDPOINT:"
)

print(
    "    /v1/images/edits"
)

print("-" * 70)

print(
    "xAI API KEY:"
)

print(
    "    XAI_API_KEY"
)

print("-" * 70)

print(
    "xAI IMAGE MODEL:"
)

print(
    "    grok-imagine-image-quality"
)

print("=" * 70)

print(
    "API BLUEPRINT: REGISTERED"
)

print("=" * 70)