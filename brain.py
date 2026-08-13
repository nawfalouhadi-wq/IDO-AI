# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL PROVIDER ROUTING
#
# TEXT:
#     XAI
#       ↓
#     MISTRAL
#       ↓
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# IMAGE UNDERSTANDING:
#     XAI
#       ↓
#     MISTRAL
#       ↓
#     GROQ
#
# IMAGE GENERATION:
#     XAI
#       ↓
#     MISTRAL
#
# IMAGE EDITING:
#     XAI
#       ↓
#     MISTRAL
#
# IMPORTANT:
#     GROQ IS A VISION FALLBACK.
#     GROQ API DOES NOT PROVIDE DIRECT IMAGE
#     GENERATION IN THE SAME WAY AS XAI.
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
# MODELS
# ============================================================

XAI_TEXT_MODEL = os.getenv(
    "XAI_TEXT_MODEL",
    "grok-4.5"
).strip()


XAI_VISION_MODEL = os.getenv(
    "XAI_VISION_MODEL",
    "grok-4.5"
).strip()


XAI_IMAGE_MODEL = os.getenv(
    "XAI_IMAGE_MODEL",
    "grok-imagine-image-quality"
).strip()


MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
).strip()


MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
).strip()


GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "qwen/qwen3.6-27b"
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
# URLS
# ============================================================

XAI_CHAT_URL = (
    "https://api.x.ai/v1/chat/completions"
)


XAI_RESPONSES_URL = (
    "https://api.x.ai/v1/responses"
)


XAI_IMAGE_URL = (
    "https://api.x.ai/v1/images/generations"
)


MISTRAL_CHAT_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


GROQ_CHAT_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
)


# ============================================================
# REQUEST SETTINGS
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv(
        "AI_REQUEST_TIMEOUT",
        "180"
    )
)


# ============================================================
# MISTRAL RETRY
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


if MISTRAL_MAX_RETRIES < 0:
    MISTRAL_MAX_RETRIES = 0


if MISTRAL_RETRY_BASE_SECONDS < 0:
    MISTRAL_RETRY_BASE_SECONDS = 0


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

4. If the user only says:
   السلام عليكم

   respond:

   وعليكم السلام ورحمة الله وبركاته،
   كيف يمكنني مساعدتك؟

5. If the greeting also contains a question,
   answer the question normally.

6. Never claim that an image was generated unless
   the image provider actually returned an image.

7. Image understanding is handled by the application's
   visual AI providers.

8. Image generation and editing are handled by the
   application's image providers.

9. Do not mention internal provider routing unless
   explicitly asked.

10. Be concise for simple questions.

11. Be detailed when the user asks for an explanation.

12. Help with programming, mathematics, translation,
    general questions and normal text tasks.
"""


# ============================================================
# GREETINGS
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
# IMAGE KEYWORDS
# ============================================================

IMAGE_GENERATION_KEYWORDS = [

    # Arabic
    "أنشئ صورة",
    "انشئ صورة",
    "أنشئ لي صورة",
    "انشئ لي صورة",
    "اصنع صورة",
    "اصنع لي صورة",
    "اعمل صورة",
    "اعمل لي صورة",
    "ولّد صورة",
    "ولد صورة",
    "ولّد لي صورة",
    "ولد لي صورة",
    "توليد صورة",
    "إنشاء صورة",
    "انشاء صورة",
    "ارسم صورة",
    "ارسم لي صورة",
    "ارسم",
    "صمم صورة",
    "صمّم صورة",
    "صمم لي صورة",
    "صمّم لي صورة",
    "أعطني صورة",
    "اعطني صورة",
    "أعطني صورة ل",
    "اعطني صورة ل",
    "أعطني صورة عن",
    "اعطني صورة عن",

    # English
    "generate an image",
    "generate image",
    "create an image",
    "create image",
    "make an image",
    "make image",
    "draw an image",
    "draw image",
    "draw a picture",
    "generate a picture",
    "create a picture",
    "generate a photo",
    "create a photo",
    "give me an image",
    "give me a picture",
    "give me a photo",
    "an image of",
    "a picture of",
    "a photo of",
    "image of",
    "picture of",
    "photo of",

    # French
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
]


IMAGE_ANALYSIS_KEYWORDS = [

    # Arabic
    "حلل الصورة",
    "حلل الصوره",
    "حلل هذه الصورة",
    "حلل هذه الصوره",
    "حلل لي الصورة",
    "حلل لي الصوره",
    "تحليل الصورة",
    "تحليل الصوره",
    "ماذا في الصورة",
    "ماذا في الصوره",
    "ماذا يظهر في الصورة",
    "ماذا يظهر في الصوره",
    "ماذا يوجد في الصورة",
    "ماذا يوجد في الصوره",
    "اشرح الصورة",
    "اشرح الصوره",
    "اشرح لي الصورة",
    "صف الصورة",
    "صف الصوره",
    "صف لي الصورة",
    "اقرأ الصورة",
    "اقرأ الصوره",
    "افحص الصورة",
    "افحص الصوره",
    "ما الموجود في الصورة",
    "ما الموجود في الصوره",
    "ما هذا في الصورة",
    "ما هذا في الصوره",
    "هل يمكنك تحليل الصورة",
    "هل تستطيع تحليل الصورة",

    # English
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
    "can you describe the image",

    # French
    "analyse l'image",
    "analyse cette image",
    "analyser l'image",
    "analyser cette image",
    "décris l'image",
    "décris cette image",
    "decris l'image",
    "decris cette image",
    "que montre l'image",
    "explique l'image",
    "explique cette image",
    "regarde l'image",
]


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


def contains_any_keyword(text, keywords):

    text = str(text or "").lower()

    for keyword in keywords:

        if keyword.lower() in text:
            return True

    return False


def is_image_generation_request(message):

    return contains_any_keyword(
        message,
        IMAGE_GENERATION_KEYWORDS
    )


def is_image_analysis_request(message):

    return contains_any_keyword(
        message,
        IMAGE_ANALYSIS_KEYWORDS
    )


def is_image_edit_request(message):

    return contains_any_keyword(
        message,
        IMAGE_EDIT_KEYWORDS
    )


def is_image_request(message):

    return (
        is_image_generation_request(message)
        or
        is_image_analysis_request(message)
    )


# ============================================================
# CLEAN IMAGE PROMPT
# ============================================================

def clean_image_prompt(message):

    text = str(message or "").strip()

    if not text:

        return (
            "Create a high-quality professional image."
        )

    prefixes = [

        "أنشئ لي صورة",
        "انشئ لي صورة",
        "أنشئ صورة",
        "انشئ صورة",

        "اصنع لي صورة",
        "اصنع صورة",

        "اعمل لي صورة",
        "اعمل صورة",

        "ولّد لي صورة",
        "ولد لي صورة",
        "ولّد صورة",
        "ولد صورة",

        "توليد صورة",
        "إنشاء صورة",
        "انشاء صورة",

        "ارسم لي صورة",
        "ارسم صورة",
        "ارسم",

        "صمم لي صورة",
        "صمّم لي صورة",
        "صمم صورة",
        "صمّم صورة",

        "أعطني صورة",
        "اعطني صورة",

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
        "generate a photo",
        "create a photo",

        "génère une image",
        "genere une image",
        "crée une image",
        "cree une image",
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

    greetings = [

        "السلام عليكم ورحمة الله وبركاته",
        "السلام عليكم ورحمه الله وبركاته",
        "السلام عليكم ورحمه الله",
        "السلام عليكم",
        "سلام عليكم",
    ]

    for greeting in greetings:

        if cleaned.startswith(greeting):

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
        "peux-tu",
        "peux tu",
    ]

    for prefix in polite_prefixes:

        if cleaned.lower().startswith(
            prefix.lower()
        ):

            cleaned = cleaned[
                len(prefix):
            ].strip()

            break

    if not cleaned:

        cleaned = text

    return cleaned


# ============================================================
# HTTP
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
# RESPONSE EXTRACTION
# ============================================================

def extract_content_text(content):

    if isinstance(content, str):

        return content.strip()

    if not isinstance(content, list):

        return ""

    parts = []

    for item in content:

        if not isinstance(item, dict):
            continue

        text = item.get("text")

        if text:
            parts.append(str(text))

    return "\n".join(parts).strip()


def extract_text_response(data):

    if not isinstance(data, dict):
        return ""

    choices = data.get("choices")

    if (
        not isinstance(choices, list)
        or not choices
    ):
        return ""

    first = choices[0]

    if not isinstance(first, dict):
        return ""

    message = first.get("message")

    if isinstance(message, dict):

        content = message.get("content")

        answer = extract_content_text(
            content
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
            "application/json",
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
            "application/json",
    }


# ============================================================
# GROQ HEADERS
# ============================================================

def groq_headers():

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )

    return {

        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json",
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

    response = safe_post(

        XAI_CHAT_URL,

        headers=xai_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "xAI HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"xAI invalid JSON: {e}"
        )

    answer = extract_text_response(data)

    if not answer:

        raise RuntimeError(
            "xAI returned an empty response."
        )

    return answer


# ============================================================
# MISTRAL TEXT
# ============================================================

def mistral_text(message):

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )

    payload = {

        "model":
            MISTRAL_VISION_MODEL,

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

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    data = response.json()

    answer = extract_text_response(data)

    if not answer:

        raise RuntimeError(
            "Mistral returned an empty response."
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

        GROQ_CHAT_URL,

        headers=groq_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Groq HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    data = response.json()

    answer = extract_text_response(data)

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

        OPENROUTER_CHAT_URL,

        headers=headers,

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "OpenRouter HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    data = response.json()

    answer = extract_text_response(data)

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
        },

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Gemini HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    data = response.json()

    candidates = data.get(
        "candidates"
    )

    if (
        not isinstance(candidates, list)
        or not candidates
    ):

        raise RuntimeError(
            "Gemini returned no candidates."
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    result = []

    for part in parts:

        if isinstance(part, dict):

            text = part.get("text")

            if text:
                result.append(str(text))

    answer = "\n".join(result).strip()

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
    ).decode("utf-8")

    safe_mime = (
        mime_type
        or "image/jpeg"
    )

    image_url = (
        f"data:{safe_mime};base64,{encoded}"
    )

    question = (
        str(message).strip()
        if message
        else
        "Analyze this image and explain what is visible."
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
                                image_url
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

        XAI_CHAT_URL,

        headers=xai_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "xAI Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )

    data = response.json()

    answer = extract_text_response(data)

    if not answer:

        raise RuntimeError(
            "xAI Vision returned an empty response."
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

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    safe_mime = (
        mime_type
        or "image/jpeg"
    )

    image_url = (
        f"data:{safe_mime};base64,{encoded}"
    )

    question = (
        str(message).strip()
        if message
        else
        "حلل هذه الصورة واشرح لي ما يظهر فيها."
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
                            image_url
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

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )

    data = response.json()

    answer = extract_text_response(data)

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

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    safe_mime = (
        mime_type
        or "image/jpeg"
    )

    image_url = (
        f"data:{safe_mime};base64,{encoded}"
    )

    question = (
        str(message).strip()
        if message
        else
        "Analyze this image and explain what is visible."
    )

    payload = {

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
                            question
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

        "temperature":
            0.3,

        "max_completion_tokens":
            4096
    }

    response = safe_post(

        GROQ_CHAT_URL,

        headers=groq_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Groq Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )

    data = response.json()

    answer = extract_text_response(data)

    if not answer:

        raise RuntimeError(
            "Groq Vision returned an empty response."
        )

    return answer


# ============================================================
# XAI IMAGE GENERATION
# ============================================================

def xai_generate_image(prompt):

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
            clean_prompt
    }

    print("=" * 70)
    print("XAI IMAGE GENERATION REQUEST")
    print("MODEL:", XAI_IMAGE_MODEL)
    print("PROMPT:", clean_prompt)
    print("=" * 70)

    response = safe_post(

        XAI_IMAGE_URL,

        headers=xai_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    print(
        "XAI IMAGE STATUS:",
        response.status_code
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "xAI Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:4000]}"
        )

    data = response.json()

    items = data.get("data")

    if (
        not isinstance(items, list)
        or not items
    ):

        raise RuntimeError(
            "xAI returned no image data."
        )

    first = items[0]

    if not isinstance(first, dict):

        raise RuntimeError(
            "xAI returned invalid image data."
        )

    image_url = first.get("url")

    if image_url:

        return {

            "image_url":
                str(image_url),

            "provider":
                "xAI",

            "model":
                XAI_IMAGE_MODEL
        }

    b64 = first.get("b64_json")

    if b64:

        return {

            "image_url":
                f"data:image/png;base64,{b64}",

            "provider":
                "xAI",

            "model":
                XAI_IMAGE_MODEL
        }

    raise RuntimeError(
        "xAI returned an image response "
        "without a usable URL."
    )


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_generate_image(prompt):

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
                        "Generate the requested image "
                        "using the image generation tool."
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

    response = safe_post(

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Mistral Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:4000]}"
        )

    data = response.json()

    image_url = find_image_url(
        data
    )

    if not image_url:

        raise RuntimeError(
            "Mistral returned no usable image."
        )

    return {

        "image_url":
            image_url,

        "provider":
            "Mistral",

        "model":
            MISTRAL_IMAGE_MODEL
    }


# ============================================================
# GENERIC IMAGE URL FINDER
# ============================================================

def find_image_url(data):

    if isinstance(data, dict):

        for key in (
            "url",
            "image_url",
            "image"
        ):

            value = data.get(key)

            if isinstance(value, str):

                if (
                    value.startswith("http://")
                    or
                    value.startswith("https://")
                    or
                    value.startswith("data:image/")
                ):

                    return value

            if isinstance(value, dict):

                nested = value.get("url")

                if nested:
                    return str(nested)

        for value in data.values():

            result = find_image_url(value)

            if result:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_image_url(item)

            if result:
                return result

    return None


# ============================================================
# XAI IMAGE EDITING
# ============================================================

def xai_edit_image(
    prompt,
    image_bytes,
    mime_type
):

    if not image_bytes:

        raise RuntimeError(
            "No source image was supplied."
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    safe_mime = (
        mime_type
        or "image/jpeg"
    )

    source_image_url = (
        f"data:{safe_mime};base64,{encoded}"
    )

    clean_prompt = clean_image_prompt(
        prompt
    )

    payload = {

        "model":
            XAI_IMAGE_MODEL,

        "prompt":
            clean_prompt,

        "image": {

            "url":
                source_image_url
        }
    }

    response = safe_post(

        XAI_IMAGE_URL,

        headers=xai_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "xAI Image Edit HTTP "
            f"{response.status_code}: "
            f"{response.text[:4000]}"
        )

    data = response.json()

    items = data.get("data")

    if (
        not isinstance(items, list)
        or not items
    ):

        raise RuntimeError(
            "xAI returned no edited image."
        )

    first = items[0]

    image_url = (
        first.get("url")
        if isinstance(first, dict)
        else None
    )

    if not image_url:

        raise RuntimeError(
            "xAI returned no edited image URL."
        )

    return {

        "image_url":
            str(image_url),

        "provider":
            "xAI",

        "model":
            XAI_IMAGE_MODEL
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

    # --------------------------------------------------------
    # First understand the source image
    # --------------------------------------------------------

    description = mistral_vision(

        (
            "Describe the supplied image accurately "
            "for image editing. Include subject, "
            "composition, objects, colors, lighting, "
            "background and important visual details. "
            "Do not invent details."
        ),

        image_bytes,

        mime_type
    )

    transformed_prompt = f"""

Create a final image based on the original image
and the user's requested modification.

ORIGINAL IMAGE DESCRIPTION:

{description}

USER REQUEST:

{prompt}

Preserve the original subject and important
visual characteristics unless the user explicitly
requests a change.

Apply the requested modification accurately.

Return the final image.
""".strip()

    return mistral_generate_image(
        transformed_prompt
    )


# ============================================================
# IMAGE GENERATION ROUTER
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
    print("IMAGE GENERATION START")
    print("PROMPT:", prompt)
    print("HAS INPUT IMAGE:", bool(image_bytes))
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # ========================================================
    # EDIT
    # ========================================================

    if image_bytes:

        print(
            "IMAGE EDIT ROUTING:"
        )

        print(
            "XAI IMAGE EDIT"
        )

        try:

            result = xai_edit_image(

                prompt,

                image_bytes,

                mime_type
            )

            return result

        except Exception as e:

            print(
                "XAI IMAGE EDIT FAILED:",
                repr(e)
            )

        print(
            "MISTRAL IMAGE EDIT"
        )

        try:

            result = mistral_edit_image(

                prompt,

                image_bytes,

                mime_type
            )

            return result

        except Exception as e:

            print(
                "MISTRAL IMAGE EDIT FAILED:",
                repr(e)
            )

        raise RuntimeError(
            "All image editing providers failed."
        )

    # ========================================================
    # GENERATION
    # ========================================================

    print(
        "IMAGE GENERATION ROUTING:"
    )

    # --------------------------------------------------------
    # XAI
    # --------------------------------------------------------

    try:

        print(
            "TRYING IMAGE PROVIDER: xAI"
        )

        return xai_generate_image(
            prompt
        )

    except Exception as e:

        print(
            "xAI IMAGE FAILED:",
            repr(e)
        )

    # --------------------------------------------------------
    # MISTRAL
    # --------------------------------------------------------

    try:

        print(
            "TRYING IMAGE PROVIDER: Mistral"
        )

        return mistral_generate_image(
            prompt
        )

    except Exception as e:

        print(
            "MISTRAL IMAGE FAILED:",
            repr(e)
        )

    raise RuntimeError(
        "All image generation providers failed."
    )


# ============================================================
# IMAGE RESPONSE
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
    print("IMAGE REQUEST")
    print("MESSAGE:", message)
    print("HAS INPUT IMAGE:", bool(image_bytes))
    print("=" * 70)

    # ========================================================
    # SOURCE IMAGE
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
                        "تم تعديل الصورة بنجاح.",

                    "imageUrl":
                        result.get(
                            "image_url",
                            ""
                        ),

                    "provider":
                        result.get(
                            "provider",
                            "xAI"
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
        # ANALYSIS
        # ----------------------------------------------------

        providers = [

            (
                "xAI Vision",
                xai_vision
            ),

            (
                "Mistral Vision",
                mistral_vision
            ),

            (
                "Groq Vision",
                groq_vision
            ),
        ]

        errors = []

        for (
            provider_name,
            provider_function
        ) in providers:

            try:

                print(
                    "TRYING IMAGE VISION:",
                    provider_name
                )

                answer = provider_function(

                    message,

                    image_bytes,

                    mime_type
                )

                if answer:

                    print(
                        "IMAGE VISION SUCCESS:",
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

                error = (
                    f"{provider_name}: {e}"
                )

                errors.append(
                    error
                )

                print(
                    "IMAGE VISION FAILED:",
                    error
                )

        return {

            "answer":
                (
                    "تعذر تحليل الصورة حاليًا. "
                    "تمت تجربة xAI وMistral وGroq."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id
        }

    # ========================================================
    # NO SOURCE IMAGE
    # ========================================================

    if is_image_analysis_request(
        message
    ):

        return {

            "answer":
                (
                    "أرسل الصورة أولًا، "
                    "ثم سأقوم بتحليلها."
                ),

            "imageUrl":
                "",

            "provider":
                "Vision",

            "conversation_id":
                conversation_id
        }

    # ========================================================
    # GENERATE
    # ========================================================

    try:

        result = (
            generate_image_with_fallbacks(

                message,

                None,

                None,

                conversation_id
            )
        )

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                result.get(
                    "image_url",
                    ""
                ),

            "provider":
                result.get(
                    "provider",
                    "xAI"
                ),

            "conversation_id":
                conversation_id
        }

    except Exception as e:

        print(
            "IMAGE GENERATION FAILED:",
            repr(e)
        )

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
    print("DYNAMIC AI RESPONSE")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
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
    # IMAGE REQUEST
    # ========================================================

    if is_image_request(
        message
    ):

        return get_image_response(

            message,

            None,

            None,

            conversation_id
        )

    # ========================================================
    # TEXT ROUTING
    # ========================================================

    providers = [

        (
            "xAI",
            xai_text
        ),

        (
            "Mistral",
            mistral_text
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
        ),
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

            error = (
                f"{provider_name}: {e}"
            )

            errors.append(
                error
            )

            print(
                "TEXT PROVIDER FAILED:",
                error
            )

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
# COMPATIBILITY
# ============================================================

def quick_response(message):

    return get_response(
        message
    )


def ask(
    message,
    conversation_id=None
):

    return get_response(

        message,

        conversation_id=conversation_id
    )


# ============================================================
# FINAL API BLUEPRINT
# ============================================================

print("=" * 70)

print("COMPATIBILITY: quick_response available")

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

print("FINAL PROVIDER ROUTING")

print("-" * 70)

print("TEXT:")
print("    XAI")
print("      ↓")
print("    MISTRAL")
print("      ↓")
print("    GROQ")
print("      ↓")
print("    OPENROUTER")
print("      ↓")
print("    GEMINI")

print("-" * 70)

print("IMAGE UNDERSTANDING:")
print("    XAI VISION")
print("      ↓")
print("    MISTRAL VISION")
print("      ↓")
print("    GROQ VISION")

print("-" * 70)

print("IMAGE GENERATION:")
print("    XAI IMAGE")
print("      ↓")
print("    MISTRAL IMAGE")

print("-" * 70)

print("IMAGE EDITING:")
print("    XAI IMAGE EDIT")
print("      ↓")
print("    MISTRAL IMAGE EDIT")

print("-" * 70)

print("GROQ:")
print("    TEXT")
print("    VISION FALLBACK")
print("    NO DIRECT IMAGE GENERATION")

print("-" * 70)

print("XAI:")
print("    TEXT")
print("    VISION")
print("    IMAGE GENERATION")
print("    IMAGE EDITING")

print("-" * 70)

print("MISTRAL:")
print("    TEXT FALLBACK")
print("    VISION FALLBACK")
print("    IMAGE GENERATION FALLBACK")
print("    IMAGE EDITING FALLBACK")

print("-" * 70)

print("MISTRAL RETRY:")
print("    ENABLED")
print("    429 -> BACKOFF")

print("=" * 70)

print("API BLUEPRINT: REGISTERED")