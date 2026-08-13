# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# PRIMARY AI:
#     GROQ
#
# TEXT:
#     GROQ
#       ↓
#     MISTRAL
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#       ↓
#     XAI
#       ↓
#     POLLINATIONS
#
# IMAGE UNDERSTANDING:
#     GROQ VISION
#       ↓
#     GEMINI
#       ↓
#     OPENROUTER
#
# IMAGE GENERATION:
#     GEMINI 3.1 FLASH IMAGE
#       ↓
#     OPENROUTER IMAGE
#       ↓
#     MISTRAL IMAGE
#
# IMPORTANT:
#     Groq does NOT pretend to generate an image.
#     Groq is the primary text/vision AI.
#
# ============================================================

import os
import re
import base64
import mimetypes
import requests

from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)


# ============================================================
# ENVIRONMENT
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
).strip()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()

XAI_API_KEY = os.getenv(
    "XAI_API_KEY",
    ""
).strip()

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY",
    ""
).strip()


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# GROQ
# ------------------------------------------------------------

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
).strip()


# ------------------------------------------------------------
# GEMINI
# ------------------------------------------------------------

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash"
).strip()

# Current native image model.
GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
).strip()


# ------------------------------------------------------------
# MISTRAL
# ------------------------------------------------------------

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-small-latest"
).strip()

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    ""
).strip()


# ------------------------------------------------------------
# OPENROUTER
# ------------------------------------------------------------

OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()

# Can be changed from Railway Variables.
OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    ""
).strip()


# ------------------------------------------------------------
# XAI
# ------------------------------------------------------------

XAI_TEXT_MODEL = os.getenv(
    "XAI_TEXT_MODEL",
    "grok-3-mini"
).strip()


# ============================================================
# API URLS
# ============================================================

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)

XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)


# ============================================================
# TIMEOUT
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv(
        "AI_REQUEST_TIMEOUT",
        "120"
    )
)


# ============================================================
# CLIENT STATUS
# ============================================================

print(
    "GROQ CLIENT:",
    "READY" if GROQ_API_KEY else "MISSING"
)

print(
    "MISTRAL CLIENT:",
    "READY" if MISTRAL_API_KEY else "MISSING"
)

print(
    "OPENROUTER CLIENT:",
    "READY" if OPENROUTER_API_KEY else "MISSING"
)

print(
    "GEMINI CLIENT:",
    "READY" if GEMINI_API_KEY else "MISSING"
)

print(
    "XAI CLIENT:",
    "READY" if XAI_API_KEY else "MISSING"
)

print(
    "POLLINATIONS CLIENT:",
    "READY" if POLLINATIONS_API_KEY else "OPTIONAL"
)

print("=" * 70)

print("GROQ TEXT MODEL:", GROQ_TEXT_MODEL)

print(
    "GROQ VISION MODEL:",
    GROQ_VISION_MODEL
)

print(
    "GEMINI IMAGE MODEL:",
    GEMINI_IMAGE_MODEL
)

print("=" * 70)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Aido AI.

You are the primary AI assistant of the application.

IMPORTANT RULES:

1. Answer naturally and directly.
2. Understand Arabic, English and French.
3. If the user says "السلام عليكم" and also asks a question,
   answer the question instead of only returning a greeting.
4. If the user says only "السلام عليكم",
   respond naturally with:
   "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك؟"
5. Never say that you cannot generate images when the application
   has an image-generation system.
6. If the user asks to create, generate, draw, make or edit an image,
   the application will route the request to the image system.
7. Do not invent API failures.
8. Do not mention internal provider routing unless asked.
9. Be concise when the user asks a simple question.
10. Be detailed when the user asks for an explanation.
"""


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_ONLY_PATTERNS = [
    r"^\s*السلام عليكم\s*[.!؟،]*\s*$",
    r"^\s*السلام عليكم ورحمة الله وبركاته\s*[.!؟،]*\s*$",
    r"^\s*سلام عليكم\s*[.!؟،]*\s*$",
]


def is_greeting_only(message):
    """
    True only when the entire message is a greeting.

    Example:

        السلام عليكم
            -> True

        السلام عليكم أنشئ لي صورة لسيارة
            -> False
    """

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


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_KEYWORDS_AR = [
    "صورة",
    "صور",
    "الصورة",
    "الصور",
    "أنشئ صورة",
    "اصنع صورة",
    "ولد صورة",
    "ولّد صورة",
    "توليد صورة",
    "إنشاء صورة",
    "ارسم",
    "ارسم لي",
    "صمم صورة",
    "تصميم صورة",
    "اعمل صورة",
    "اعمل لي صورة",
    "أنشئ لي صورة",
    "اصنع لي صورة",
    "عدّل الصورة",
    "تعديل الصورة",
    "عدل الصورة",
    "حرر الصورة",
    "تحرير الصورة",
]

IMAGE_KEYWORDS_EN = [
    "generate an image",
    "generate image",
    "create an image",
    "create image",
    "make an image",
    "make image",
    "draw an image",
    "draw image",
    "edit the image",
    "edit image",
    "modify the image",
    "modify image",
    "image generation",
    "picture",
    "photo",
    "render an image",
]

IMAGE_KEYWORDS_FR = [
    "génère une image",
    "genere une image",
    "crée une image",
    "cree une image",
    "faire une image",
    "dessine une image",
    "modifier l'image",
    "modifie l'image",
]


def is_image_request(message):
    """
    Detect whether the user is asking for image generation/editing.
    """

    if not message:
        return False

    text = str(message).strip().lower()

    # --------------------------------------------------------
    # Arabic
    # --------------------------------------------------------

    for keyword in IMAGE_KEYWORDS_AR:

        if keyword.lower() in text:
            return True

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    for keyword in IMAGE_KEYWORDS_EN:

        if keyword.lower() in text:
            return True

    # --------------------------------------------------------
    # French
    # --------------------------------------------------------

    for keyword in IMAGE_KEYWORDS_FR:

        if keyword.lower() in text:
            return True

    return False


# ============================================================
# CLEAN IMAGE PROMPT
# ============================================================

def clean_image_prompt(message):
    """
    Convert the user's complete request into a clean image prompt.

    We intentionally keep the actual request instead of allowing
    a text model to answer it as ordinary chat.
    """

    text = str(message or "").strip()

    if not text:
        return (
            "Create a high-quality professional image "
            "based on the user's request."
        )

    # Remove common conversational prefixes.
    prefixes = [
        "أنشئ لي",
        "انشئ لي",
        "اصنع لي",
        "اعمل لي",
        "ولد لي",
        "ولّد لي",
        "أنشئ",
        "انشئ",
        "اصنع",
        "اعمل",
        "ولّد",
        "ولد",
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

    if not cleaned:
        cleaned = text

    return cleaned


# ============================================================
# HTTP HELPER
# ============================================================

def safe_post(
    url,
    headers=None,
    json_data=None,
    data=None,
    timeout=REQUEST_TIMEOUT
):

    response = requests.post(
        url,
        headers=headers or {},
        json=json_data,
        data=data,
        timeout=timeout
    )

    return response


# ============================================================
# EXTRACT TEXT FROM OPENAI-COMPATIBLE RESPONSE
# ============================================================

def extract_text_response(data):

    if not isinstance(data, dict):
        return ""

    choices = data.get("choices")

    if not choices:
        return ""

    first = choices[0]

    message = first.get(
        "message",
        {}
    )

    content = message.get(
        "content"
    )

    if isinstance(
        content,
        str
    ):
        return content.strip()

    if isinstance(
        content,
        list
    ):

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

    return ""


# ============================================================
# GREETING RESPONSE
# ============================================================

def greeting_response():

    return (
        "وعليكم السلام ورحمة الله وبركاته، "
        "كيف يمكنني مساعدتك؟"
    )


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text(message):

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )

    headers = {
        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "model":
            GROQ_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content":
                    message,
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096,
    }

    response = safe_post(
        GROQ_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Groq HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    answer = extract_text_response(
        data
    )

    if not answer:

        raise RuntimeError(
            "Groq returned an empty response."
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

    image_url = (
        f"data:{mime_type};base64,{encoded}"
    )

    headers = {
        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "model":
            GROQ_VISION_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            message,
                    },

                    {
                        "type":
                            "image_url",

                        "image_url": {
                            "url":
                                image_url
                        },
                    }
                ],
            }
        ],

        "temperature":
            0.5,

        "max_tokens":
            4096,
    }

    response = safe_post(
        GROQ_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Groq Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    answer = extract_text_response(
        data
    )

    if not answer:

        raise RuntimeError(
            "Groq Vision returned empty response."
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

    headers = {

        "Authorization":
            f"Bearer {MISTRAL_API_KEY}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "model":
            MISTRAL_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content":
                    message,
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096,
    }

    response = safe_post(
        MISTRAL_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Mistral HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    answer = extract_text_response(
        response.json()
    )

    if not answer:
        raise RuntimeError(
            "Mistral returned empty response."
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
            "IDO AI",
    }

    payload = {

        "model":
            OPENROUTER_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content":
                    message,
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096,
    }

    response = safe_post(
        OPENROUTER_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"OpenRouter HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    answer = extract_text_response(
        response.json()
    )

    if not answer:
        raise RuntimeError(
            "OpenRouter returned empty response."
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
        f"{GEMINI_URL}/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    headers = {
        "Content-Type":
            "application/json"
    }

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
                            message
                    }
                ]
            }
        ]
    }

    response = safe_post(
        url,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Gemini HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    candidates = data.get(
        "candidates",
        []
    )

    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates."
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    text_parts = []

    for part in parts:

        if "text" in part:

            text_parts.append(
                part["text"]
            )

    answer = "\n".join(
        text_parts
    ).strip()

    if not answer:
        raise RuntimeError(
            "Gemini returned empty text."
        )

    return answer


# ============================================================
# XAI TEXT
# ============================================================

def xai_text(message):

    if not XAI_API_KEY:
        raise RuntimeError(
            "XAI_API_KEY is missing."
        )

    headers = {

        "Authorization":
            f"Bearer {XAI_API_KEY}",

        "Content-Type":
            "application/json",
    }

    payload = {

        "model":
            XAI_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content":
                    message,
            }
        ],

        "temperature":
            0.7,

        "max_tokens":
            4096,
    }

    response = safe_post(
        XAI_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"xAI HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    answer = extract_text_response(
        response.json()
    )

    if not answer:
        raise RuntimeError(
            "xAI returned empty response."
        )

    return answer


# ============================================================
# POLLINATIONS TEXT FALLBACK
# ============================================================

def pollinations_text(message):

    url = (
        "https://text.pollinations.ai/"
        + requests.utils.quote(
            message
        )
    )

    headers = {}

    if POLLINATIONS_API_KEY:

        headers[
            "Authorization"
        ] = (
            f"Bearer {POLLINATIONS_API_KEY}"
        )

    response = requests.get(
        url,
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Pollinations HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    answer = response.text.strip()

    if not answer:

        raise RuntimeError(
            "Pollinations returned empty response."
        )

    return answer


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def gemini_generate_image(
    prompt,
    image_bytes=None,
    mime_type=None
):

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    url = (
        f"{GEMINI_URL}/"
        f"{GEMINI_IMAGE_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    headers = {
        "Content-Type":
            "application/json"
    }

    parts = []

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    parts.append({

        "text":
            (
                "Create or edit the image according "
                "to this user's request. "
                "Return the generated image.\n\n"
                f"USER REQUEST:\n{prompt}"
            )
    })

    # --------------------------------------------------------
    # Existing image for editing
    # --------------------------------------------------------

    if image_bytes:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        parts.append({

            "inline_data": {

                "mime_type":
                    mime_type or "image/jpeg",

                "data":
                    encoded,
            }
        })

    payload = {

        "contents": [

            {
                "role":
                    "user",

                "parts":
                    parts,
            }
        ],

        "generationConfig": {

            "responseModalities": [
                "TEXT",
                "IMAGE"
            ],

            "imageConfig": {

                "aspectRatio":
                    "1:1",

                "imageSize":
                    "1K",
            }
        }
    }

    response = safe_post(
        url,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Gemini Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()

    candidates = data.get(
        "candidates",
        []
    )

    if not candidates:

        raise RuntimeError(
            "Gemini Image returned no candidates."
        )

    response_parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    generated_text = []

    for part in response_parts:

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        inline = part.get(
            "inlineData"
        )

        if inline is None:

            inline = part.get(
                "inline_data"
            )

        if inline:

            image_data = inline.get(
                "data"
            )

            generated_mime = inline.get(
                "mimeType",
                inline.get(
                    "mime_type",
                    "image/png"
                )
            )

            if image_data:

                # ------------------------------------------------
                # Return a DATA URL.
                #
                # This is important because app.py already expects
                # IMAGE_URL:<value>.
                # ------------------------------------------------

                data_url = (
                    f"data:{generated_mime};base64,"
                    f"{image_data}"
                )

                return {
                    "image_url":
                        data_url,

                    "text":
                        "\n".join(
                            generated_text
                        ).strip(),

                    "provider":
                        "Gemini",

                    "model":
                        GEMINI_IMAGE_MODEL,
                }

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        text = part.get(
            "text"
        )

        if text:

            generated_text.append(
                str(text)
            )

    raise RuntimeError(
        "Gemini completed the request "
        "but did not return image data."
    )


# ============================================================
# OPENROUTER IMAGE GENERATION
# ============================================================

def openrouter_generate_image(
    prompt,
    image_bytes=None,
    mime_type=None
):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing."
        )

    if not OPENROUTER_IMAGE_MODEL:

        raise RuntimeError(
            "OPENROUTER_IMAGE_MODEL is not configured."
        )

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
            "IDO AI",
    }

    content = [

        {
            "type":
                "text",

            "text":
                prompt,
        }
    ]

    # --------------------------------------------------------
    # Optional image input
    # --------------------------------------------------------

    if image_bytes:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        content.append({

            "type":
                "image_url",

            "image_url": {

                "url":
                    (
                        f"data:"
                        f"{mime_type or 'image/jpeg'}"
                        f";base64,"
                        f"{encoded}"
                    )
            }
        })

    payload = {

        "model":
            OPENROUTER_IMAGE_MODEL,

        "messages": [

            {
                "role":
                    "user",

                "content":
                    content,
            }
        ],

        "modalities": [
            "text",
            "image"
        ],
    }

    response = safe_post(
        OPENROUTER_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"OpenRouter Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()

    choices = data.get(
        "choices",
        []
    )

    if not choices:

        raise RuntimeError(
            "OpenRouter Image returned no choices."
        )

    message = choices[0].get(
        "message",
        {}
    )

    content_response = message.get(
        "content"
    )

    # --------------------------------------------------------
    # Content can contain image objects.
    # --------------------------------------------------------

    if isinstance(
        content_response,
        list
    ):

        text_parts = []

        for item in content_response:

            if not isinstance(
                item,
                dict
            ):
                continue

            image_url = item.get(
                "image_url"
            )

            if isinstance(
                image_url,
                dict
            ):

                url = image_url.get(
                    "url"
                )

                if url:

                    return {
                        "image_url":
                            url,

                        "text":
                            "\n".join(
                                text_parts
                            ),

                        "provider":
                            "OpenRouter",

                        "model":
                            OPENROUTER_IMAGE_MODEL,
                    }

            text = item.get(
                "text"
            )

            if text:
                text_parts.append(
                    str(text)
                )

    raise RuntimeError(
        "OpenRouter did not return image data."
    )


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_generate_image(
    prompt,
    image_bytes=None,
    mime_type=None
):

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )

    if not MISTRAL_IMAGE_MODEL:

        raise RuntimeError(
            "MISTRAL_IMAGE_MODEL is not configured."
        )

    # --------------------------------------------------------
    # Mistral image APIs may vary by account/API version.
    # Keep this endpoint configurable.
    # --------------------------------------------------------

    mistral_image_url = os.getenv(
        "MISTRAL_IMAGE_URL",
        "https://api.mistral.ai/v1/images/generations"
    )

    headers = {

        "Authorization":
            f"Bearer {MISTRAL_API_KEY}",
    }

    payload = {

        "model":
            MISTRAL_IMAGE_MODEL,

        "prompt":
            prompt,

        "n":
            1,

        "size":
            "1024x1024",
    }

    response = safe_post(
        mistral_image_url,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Mistral Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()

    images = data.get(
        "data",
        []
    )

    if not images:

        raise RuntimeError(
            "Mistral Image returned no images."
        )

    first = images[0]

    url = first.get(
        "url"
    )

    if url:

        return {
            "image_url":
                url,

            "text":
                "",

            "provider":
                "Mistral",

            "model":
                MISTRAL_IMAGE_MODEL,
        }

    b64 = first.get(
        "b64_json"
    )

    if b64:

        return {
            "image_url":
                (
                    "data:image/png;base64,"
                    + b64
                ),

            "text":
                "",

            "provider":
                "Mistral",

            "model":
                MISTRAL_IMAGE_MODEL,
        }

    raise RuntimeError(
        "Mistral returned an image "
        "without URL or base64 data."
    )


# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================

def gemini_vision(
    message,
    image_bytes,
    mime_type
):

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    url = (
        f"{GEMINI_URL}/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    headers = {
        "Content-Type":
            "application/json"
    }

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
                            message
                    },

                    {
                        "inline_data": {

                            "mime_type":
                                mime_type,

                            "data":
                                encoded,
                        }
                    }
                ]
            }
        ]
    }

    response = safe_post(
        url,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Gemini Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()

    candidates = data.get(
        "candidates",
        []
    )

    if not candidates:

        raise RuntimeError(
            "Gemini Vision returned no candidates."
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    texts = []

    for part in parts:

        text = part.get(
            "text"
        )

        if text:
            texts.append(
                str(text)
            )

    answer = "\n".join(
        texts
    ).strip()

    if not answer:

        raise RuntimeError(
            "Gemini Vision returned empty text."
        )

    return answer


# ============================================================
# OPENROUTER VISION
# ============================================================

def openrouter_vision(
    message,
    image_bytes,
    mime_type
):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing."
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_url = (
        f"data:{mime_type};base64,{encoded}"
    )

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
            "IDO AI",
    }

    payload = {

        "model":
            OPENROUTER_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    SYSTEM_PROMPT,
            },

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            message,
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
            4096,
    }

    response = safe_post(
        OPENROUTER_URL,
        headers=headers,
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"OpenRouter Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    answer = extract_text_response(
        response.json()
    )

    if not answer:

        raise RuntimeError(
            "OpenRouter Vision returned empty response."
        )

    return answer


# ============================================================
# TEXT RESPONSE
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    message = str(
        message or ""
    ).strip()

    if not message:

        return (
            "اكتب رسالة أولًا."
        )

    print("=" * 70)
    print("DYNAMIC AI RESPONSE")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # --------------------------------------------------------
    # Greeting ONLY
    # --------------------------------------------------------

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
                conversation_id,
        }

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # If this is an image request, DO NOT send it to Groq
    # as an ordinary text question.
    #
    # Route it to image generation.
    # --------------------------------------------------------

    if is_image_request(
        message
    ):

        print(
            "IMAGE REQUEST DETECTED FROM TEXT"
        )

        result = get_image_response(
            message,
            None,
            None,
            conversation_id=conversation_id
        )

        if isinstance(
            result,
            dict
        ):

            return result

        if isinstance(
            result,
            str
        ):

            if result.startswith(
                "IMAGE_URL:"
            ):

                return {
                    "answer":
                        "تم إنشاء الصورة بنجاح.",

                    "imageUrl":
                        result[
                            len("IMAGE_URL:"):
                        ].strip(),

                    "provider":
                        "Image Generator",

                    "conversation_id":
                        conversation_id,
                }

            return {
                "answer":
                    result,

                "imageUrl":
                    "",

                "provider":
                    "Image Generator",

                "conversation_id":
                    conversation_id,
            }

    # --------------------------------------------------------
    # PRIMARY: GROQ
    # --------------------------------------------------------

    providers = [

        (
            "Groq",
            groq_text
        ),

        (
            "Mistral",
            mistral_text
        ),

        (
            "OpenRouter",
            openrouter_text
        ),

        (
            "Gemini",
            gemini_text
        ),

        (
            "xAI",
            xai_text
        ),

        (
            "Pollinations",
            pollinations_text
        ),
    ]

    errors = []

    for provider_name, provider_function in providers:

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
                        conversation_id,
                }

        except Exception as e:

            error_text = (
                f"{provider_name}: {e}"
            )

            errors.append(
                error_text
            )

            print(
                "TEXT PROVIDER FAILED:",
                error_text
            )

    # --------------------------------------------------------
    # Everything failed
    # --------------------------------------------------------

    print(
        "ALL TEXT PROVIDERS FAILED"
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
            conversation_id,
    }


# ============================================================
# IMAGE RESPONSE
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

    print("=" * 70)
    print("IMAGE REQUEST")
    print("MESSAGE:", message)
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
    # CASE 1:
    # USER UPLOADED AN IMAGE
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # If the user explicitly asks to edit/generate an image,
        # use the IMAGE GENERATION route.
        # ----------------------------------------------------

        if is_image_request(
            message
        ):

            print(
                "IMAGE EDIT REQUEST DETECTED"
            )

            return generate_image_with_fallbacks(
                message,
                image_bytes,
                mime_type
            )

        # ----------------------------------------------------
        # Otherwise this is image understanding.
        #
        # PRIMARY:
        #     Groq Vision
        #
        # FALLBACK:
        #     Gemini
        #
        # FALLBACK:
        #     OpenRouter
        # ----------------------------------------------------

        vision_providers = [

            (
                "Groq Vision",
                lambda:
                    groq_vision(
                        message,
                        image_bytes,
                        mime_type
                    )
            ),

            (
                "Gemini Vision",
                lambda:
                    gemini_vision(
                        message,
                        image_bytes,
                        mime_type
                    )
            ),

            (
                "OpenRouter Vision",
                lambda:
                    openrouter_vision(
                        message,
                        image_bytes,
                        mime_type
                    )
            ),
        ]

        for provider_name, provider_function in vision_providers:

            try:

                print(
                    "TRYING VISION PROVIDER:",
                    provider_name
                )

                answer = provider_function()

                if answer:

                    print(
                        "VISION PROVIDER SUCCESS:",
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
                            conversation_id,
                    }

            except Exception as e:

                print(
                    "VISION PROVIDER FAILED:",
                    provider_name,
                    repr(e)
                )

        return {
            "answer":
                (
                    "تعذر تحليل الصورة حاليًا."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id,
        }

    # ========================================================
    # CASE 2:
    # TEXT IMAGE GENERATION
    # ========================================================

    return generate_image_with_fallbacks(
        message,
        None,
        None,
        conversation_id=conversation_id
    )


# ============================================================
# IMAGE GENERATION FALLBACK SYSTEM
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
    print("=" * 70)

    image_providers = [

        # ----------------------------------------------------
        # PRIMARY IMAGE GENERATOR
        # ----------------------------------------------------

        (
            "Gemini Image",
            lambda:
                gemini_generate_image(
                    prompt,
                    image_bytes,
                    mime_type
                )
        ),

        # ----------------------------------------------------
        # SECONDARY IMAGE GENERATOR
        # ----------------------------------------------------

        (
            "OpenRouter Image",
            lambda:
                openrouter_generate_image(
                    prompt,
                    image_bytes,
                    mime_type
                )
        ),

        # ----------------------------------------------------
        # THIRD IMAGE GENERATOR
        # ----------------------------------------------------

        (
            "Mistral Image",
            lambda:
                mistral_generate_image(
                    prompt,
                    image_bytes,
                    mime_type
                )
        ),
    ]

    errors = []

    for provider_name, provider_function in image_providers:

        try:

            print(
                "TRYING IMAGE PROVIDER:",
                provider_name
            )

            result = provider_function()

            if not isinstance(
                result,
                dict
            ):
                raise RuntimeError(
                    "Invalid image provider response."
                )

            image_url = result.get(
                "image_url"
            )

            if not image_url:

                raise RuntimeError(
                    "Provider returned no image URL/data."
                )

            print(
                "IMAGE GENERATION SUCCESS:",
                provider_name
            )

            print(
                "IMAGE URL TYPE:",
                (
                    "DATA URL"
                    if image_url.startswith(
                        "data:"
                    )
                    else "REMOTE URL"
                )
            )

            answer_text = result.get(
                "text"
            )

            if not answer_text:

                answer_text = (
                    "تم إنشاء الصورة بنجاح."
                )

            return {

                "answer":
                    answer_text,

                "imageUrl":
                    image_url,

                "provider":
                    provider_name,

                "conversation_id":
                    conversation_id,
            }

        except Exception as e:

            error_text = (
                f"{provider_name}: {e}"
            )

            errors.append(
                error_text
            )

            print(
                "IMAGE PROVIDER FAILED:",
                error_text
            )

    # ========================================================
    # ALL IMAGE PROVIDERS FAILED
    # ========================================================

    print("=" * 70)
    print("ALL IMAGE PROVIDERS FAILED")
    print("=" * 70)

    for error in errors:

        print(
            "IMAGE ERROR:",
            error
        )

    return {

        "answer":
            (
                "تعذر إنشاء الصورة حاليًا. "
                "تمت تجربة مولدات الصور المتاحة "
                "تلقائيًا، ولكن لم يُرجع أي مولد صورة."
            ),

        "imageUrl":
            "",

        "provider":
            None,

        "conversation_id":
            conversation_id,
    }


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message
):

    """
    Compatibility function.

    Some older versions of app.py/API.py call:
        quick_response(message)
    """

    return get_response(
        message
    )


# ============================================================
# OPTIONAL SIMPLE CHAT FUNCTION
# ============================================================

def ask(
    message,
    conversation_id=None
):

    return get_response(
        message,
        conversation_id=conversation_id
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
    "VISION ROUTE:"
)

print(
    "    GROQ VISION -> GEMINI -> OPENROUTER"
)

print(
    "IMAGE GENERATION:"
)

print(
    "    GEMINI IMAGE -> OPENROUTER IMAGE -> MISTRAL IMAGE"
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
    "    SMART GREETING DETECTION ENABLED"
)

print("=" * 68)