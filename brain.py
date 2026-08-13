# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# ============================================================
# FINAL PROVIDER ROUTING
# ============================================================
#
# TEXT:
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# IMAGES:
#     MISTRAL ONLY
#
#     ├── IMAGE ANALYSIS
#     ├── IMAGE GENERATION
#     └── IMAGE EDITING
#
# ============================================================
#
# IMPORTANT:
#
# GROQ:
#     TEXT ONLY
#
# OPENROUTER:
#     TEXT ONLY
#
# GEMINI:
#     TEXT ONLY
#
# MISTRAL:
#     IMAGES ONLY
#
# ============================================================

import os
import re
import base64
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


MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()


# ============================================================
# TEXT MODELS
# ============================================================

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
# MISTRAL MODELS
# ============================================================

# Image understanding / Vision

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
).strip()


# Image generation

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
).strip()


# ============================================================
# API URLS
# ============================================================

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
# CLIENT STATUS
# ============================================================

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

print(
    "MISTRAL CLIENT:",
    "READY" if MISTRAL_API_KEY else "MISSING"
)


print("=" * 70)

print(
    "GROQ TEXT MODEL:",
    GROQ_TEXT_MODEL
)

print(
    "OPENROUTER TEXT MODEL:",
    OPENROUTER_TEXT_MODEL
)

print(
    "GEMINI TEXT MODEL:",
    GEMINI_TEXT_MODEL
)

print(
    "MISTRAL VISION MODEL:",
    MISTRAL_VISION_MODEL
)

print(
    "MISTRAL IMAGE MODEL:",
    MISTRAL_IMAGE_MODEL
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

6. Never pretend to generate an image using text only.

7. Image generation, image editing and image understanding
   are handled by the application's Mistral image system.

8. Do not claim an image was generated unless the image
   system actually returned an image.

9. Do not mention internal provider routing unless
   explicitly asked.

10. Be concise for simple questions.

11. Be detailed when the user asks for an explanation.

12. Help with programming, mathematics, translation,
    general questions, explanations and normal text tasks.
"""


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_ONLY_PATTERNS = [

    r"^\s*السلام عليكم\s*[.!؟،]*\s*$",

    r"^\s*السلام عليكم ورحمة الله وبركاته\s*[.!؟،]*\s*$",

    r"^\s*سلام عليكم\s*[.!؟،]*\s*$",
]


def is_greeting_only(
    message
):

    if not message:

        return False

    text = str(
        message
    ).strip()

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

    "توليد صوره",
    "إنشاء صوره",

    "ارسم",
    "ارسم لي",
    "ارسم صورة",
    "ارسم لي صورة",

    "صمم صورة",
    "صمّم صورة",
    "تصميم صورة",

    "صورة",
    "صور",

    "أنشئ رسمة",
    "انشئ رسمة",

    "اصنع رسمة",
    "اعمل رسمة",

    "عدّل الصورة",
    "عدل الصورة",

    "عدّل هذه الصورة",
    "عدل هذه الصورة",

    "تعديل الصورة",
    "تحرير الصورة",

    "حرر الصورة",
    "حرّر الصورة",

    "غيّر الصورة",
    "غير الصورة",

    "غيّر هذه الصورة",
    "غير هذه الصورة",

    "أضف إلى الصورة",
    "اضف الى الصورة",

    "أضف للصورة",
    "اضف للصورة",

    "احذف من الصورة",
    "احذف شيء من الصورة",

    "استبدل في الصورة",
    "استبدل الصورة",
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

    "draw a picture",
    "draw picture",

    "generate a picture",
    "create a picture",

    "generate a photo",
    "create a photo",

    "make a picture",
    "make a photo",

    "edit the image",
    "edit image",

    "edit this image",

    "modify the image",
    "modify image",

    "modify this image",

    "change the image",
    "change this image",

    "remove from the image",
    "add to the image",

    "replace in the image",

    "image generation",
]


IMAGE_KEYWORDS_FR = [

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

    "modifier l'image",
    "modifie l'image",

    "modifier cette image",
    "modifie cette image",

    "changer l'image",
    "change l'image",
]


def is_image_request(
    message
):

    if not message:

        return False

    text = str(
        message
    ).strip().lower()

    for keyword in IMAGE_KEYWORDS_AR:

        if keyword.lower() in text:

            return True

    for keyword in IMAGE_KEYWORDS_EN:

        if keyword.lower() in text:

            return True

    for keyword in IMAGE_KEYWORDS_FR:

        if keyword.lower() in text:

            return True

    return False


# ============================================================
# IMAGE EDIT DETECTION
# ============================================================

def is_image_edit_request(
    message
):

    if not message:

        return False

    text = str(
        message
    ).strip().lower()

    edit_keywords = [

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

        "عدلها",

        "عدّلها",

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

    for keyword in edit_keywords:

        if keyword.lower() in text:

            return True

    return False


# ============================================================
# CLEAN IMAGE PROMPT
# ============================================================

def clean_image_prompt(
    message
):

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

        "أنشئ لي",
        "انشئ لي",

        "أنشئ",
        "انشئ",

        "اصنع لي صورة",
        "اصنع لي",

        "اصنع صورة",
        "اصنع",

        "اعمل لي صورة",
        "اعمل لي",

        "اعمل صورة",
        "اعمل",

        "ولّد لي صورة",
        "ولد لي صورة",

        "ولّد صورة",
        "ولد صورة",

        "ولّد لي",
        "ولد لي",

        "ولّد",
        "ولد",

        "ارسم لي صورة",
        "ارسم صورة",

        "ارسم لي",
        "ارسم",

        "صمم صورة",
        "صمّم صورة",

        "صمم",
        "صمّم",

        "توليد صورة",
        "إنشاء صورة",

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

    # --------------------------------------------------------
    # Remove common greeting prefix from image prompts.
    # --------------------------------------------------------

    greeting_prefixes = [

        "السلام عليكم",
        "السلام عليكم ورحمة الله وبركاته",
        "سلام عليكم",
        "السلام عليكم ورحمه الله",
    ]

    for greeting in greeting_prefixes:

        if cleaned.startswith(
            greeting
        ):

            cleaned = cleaned[
                len(greeting):
            ].strip()

            break

    if not cleaned:

        cleaned = text

    return cleaned


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
# CONTENT TEXT EXTRACTION
# ============================================================

def extract_content_text(
    content
):

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

        item_type = item.get(
            "type"
        )

        if item_type == "text":

            text = item.get(
                "text"
            )

            if text:

                parts.append(
                    str(text)
                )

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


# ============================================================
# OPENAI-COMPATIBLE TEXT EXTRACTOR
# ============================================================

def extract_text_response(
    data
):

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

    # --------------------------------------------------------
    # Standard message
    # --------------------------------------------------------

    message = first.get(
        "message"
    )

    if isinstance(
        message,
        dict
    ):

        content = message.get(
            "content"
        )

        answer = extract_content_text(
            content
        )

        if answer:

            return answer

    # --------------------------------------------------------
    # Mistral tool-message response
    #
    # choices[0].messages
    # --------------------------------------------------------

    messages = first.get(
        "messages"
    )

    if isinstance(
        messages,
        list
    ):

        parts = []

        for item in messages:

            if not isinstance(
                item,
                dict
            ):

                continue

            content = item.get(
                "content"
            )

            answer = extract_content_text(
                content
            )

            if answer:

                parts.append(
                    answer
                )

        if parts:

            return "\n".join(
                parts
            ).strip()

    return ""


# ============================================================
# MISTRAL IMAGE REFERENCE EXTRACTION
# ============================================================

def extract_mistral_image_reference(
    data
):
    """
    Supports:
        direct image URLs
        [Image: https://...]
        image_url objects
        tool_file
        file_id
        nested choices/messages/content
    """

    if not isinstance(
        data,
        (dict, list)
    ):

        return None


    def walk(
        value
    ):

        # ====================================================
        # DICTIONARY
        # ====================================================

        if isinstance(
            value,
            dict
        ):

            # ------------------------------------------------
            # Explicit tool_file
            # ------------------------------------------------

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


            # ------------------------------------------------
            # Generic file_id
            # ------------------------------------------------

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


            # ------------------------------------------------
            # image_url as string
            # ------------------------------------------------

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
                    or
                    image_url.startswith(
                        "data:image/"
                    )
                ):

                    return {

                        "type":
                            "url",

                        "value":
                            image_url
                    }


            # ------------------------------------------------
            # image_url as object
            # ------------------------------------------------

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


            # ------------------------------------------------
            # Direct URL fields
            # ------------------------------------------------

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
                        or
                        item.startswith(
                            "data:image/"
                        )
                    ):

                        return {

                            "type":
                                "url",

                            "value":
                                item
                        }


            # ------------------------------------------------
            # Text containing an image URL
            #
            # Example:
            # [Image: https://files.mistral.ai/...]
            # ------------------------------------------------

            text = value.get(
                "text"
            )

            if isinstance(
                text,
                str
            ):

                match = re.search(

                    r"https?://[^\s\]\)>]+",

                    text
                )

                if match:

                    url = match.group(
                        0
                    ).rstrip(
                        ".,;)]}>"
                    )

                    return {

                        "type":
                            "url",

                        "value":
                            url
                    }


            # ------------------------------------------------
            # Recursive known fields
            # ------------------------------------------------

            for key in (
                "content",
                "messages",
                "choices",
                "outputs",
                "output",
                "response"
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


            # ------------------------------------------------
            # Last recursive pass
            # ------------------------------------------------

            for child in value.values():

                result = walk(
                    child
                )

                if result:

                    return result


        # ====================================================
        # LIST
        # ====================================================

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

def groq_text(
    message
):

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
                    message
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
            f"{response.text[:1500]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "Groq returned invalid JSON: "
            f"{e}"
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

def openrouter_text(
    message
):

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
                    message
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
            f"{response.text[:1500]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "OpenRouter returned invalid JSON: "
            f"{e}"
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

def gemini_text(
    message
):

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
            f"{response.text[:1800]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "Gemini returned invalid JSON: "
            f"{e}"
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

    if not isinstance(
        first,
        dict
    ):

        raise RuntimeError(
            "Gemini returned an invalid candidate."
        )

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
# MISTRAL VISION
# ============================================================

def mistral_vision(
    message,
    image_bytes,
    mime_type
):
    """
    Mistral-only image understanding.

    Uses Mistral Vision through Chat Completions.
    """

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
        f"data:{safe_mime};base64,{encoded}"
    )

    question = (

        str(
            message
        ).strip()

        if message

        else
        "حلل هذه الصورة واشرح لي بالتفصيل ما الذي يظهر فيها."
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

    print("=" * 70)

    print(
        "MISTRAL VISION REQUEST"
    )

    print(
        "MODEL:",
        MISTRAL_VISION_MODEL
    )

    print(
        "MIME TYPE:",
        safe_mime
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print(
        "QUESTION:",
        question
    )

    print("=" * 70)

    response = safe_post(

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    print(
        "MISTRAL VISION STATUS:",
        response.status_code
    )

    if response.status_code >= 400:

        print(
            "MISTRAL VISION ERROR:"
        )

        print(
            response.text[:5000]
        )

        raise RuntimeError(
            "Mistral Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "Mistral Vision returned invalid JSON: "
            f"{e}"
        )

    answer = extract_text_response(
        data
    )

    if not answer:

        print(
            "MISTRAL VISION JSON:"
        )

        print(
            str(data)[:7000]
        )

        raise RuntimeError(
            "Mistral Vision returned an empty response."
        )

    print(
        "MISTRAL VISION SUCCESS"
    )

    return answer


# ============================================================
# MISTRAL FILE SIGNED URL
# ============================================================

def mistral_file_signed_url(
    file_id,
    expiry_hours=24
):
    """
    Convert a Mistral file_id into a temporary signed URL.
    """

    if not file_id:

        return None

    safe_expiry = max(
        1,
        min(
            int(
                expiry_hours
            ),
            168
        )
    )

    url = (
        f"{MISTRAL_FILES_URL}/"
        f"{file_id}/url"
    )

    response = safe_get(

        url,

        headers=mistral_headers(),

        params={
            "expiry":
                safe_expiry
        },

        timeout=REQUEST_TIMEOUT
    )

    print(
        "MISTRAL FILE URL STATUS:",
        response.status_code
    )

    if response.status_code >= 400:

        print(
            "MISTRAL FILE URL ERROR:"
        )

        print(
            response.text[:5000]
        )

        raise RuntimeError(
            "Mistral File URL HTTP "
            f"{response.status_code}: "
            f"{response.text[:2500]}"
        )

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "Mistral File URL returned invalid JSON: "
            f"{e}"
        )

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
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_generate_image(
    prompt
):
    """
    Mistral-only image generation.

    IMPORTANT:
        tool_choice = "required"

    This forces Mistral to call the available image
    generation tool instead of answering with text.

    Mistral documents:
        tools=[{"type": "image_generation"}]

    and:
        tool_choice="required"

    as the mechanism for forcing tool use.
    """

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing."
        )

    clean_prompt = clean_image_prompt(
        prompt
    )

    if not clean_prompt:

        clean_prompt = (
            "Create a high-quality professional image."
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
                        "You are Aido AI's image "
                        "generation system. "
                        "For this request you MUST use "
                        "the image_generation tool. "
                        "Do not answer with a normal text "
                        "response. "
                        "Do not ask the user for more "
                        "details if the image request is "
                        "already understandable. "
                        "Generate the requested image."
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

        # ====================================================
        # CRITICAL FIX
        # ====================================================

        "tool_choice":
            "required",

        "temperature":
            0.3
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
        "TOOL:",
        "image_generation"
    )

    print(
        "TOOL CHOICE:",
        "required"
    )

    print(
        "PROMPT:",
        clean_prompt
    )

    print("=" * 70)

    response = safe_post(

        MISTRAL_CHAT_URL,

        headers=mistral_headers(),

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    print(
        "MISTRAL IMAGE STATUS:",
        response.status_code
    )

    if response.status_code >= 400:

        print(
            "MISTRAL IMAGE ERROR RESPONSE:"
        )

        print(
            response.text[:7000]
        )

        raise RuntimeError(
            "Mistral Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:3000]}"
        )

    try:

        data = response.json()

    except Exception as e:

        print(
            "MISTRAL IMAGE RAW RESPONSE:"
        )

        print(
            response.text[:7000]
        )

        raise RuntimeError(
            "Mistral Image returned invalid JSON: "
            f"{e}"
        )

    # ========================================================
    # COMPLETE RAW RESPONSE LOG
    # ========================================================

    print(
        "MISTRAL IMAGE JSON:"
    )

    print(
        str(data)[:12000]
    )

    # ========================================================
    # FIND IMAGE REFERENCE
    # ========================================================

    reference = (
        extract_mistral_image_reference(
            data
        )
    )

    if not reference:

        # ----------------------------------------------------
        # Check whether the model still returned text only.
        # ----------------------------------------------------

        text_answer = extract_text_response(
            data
        )

        if text_answer:

            raise RuntimeError(
                "Mistral returned text instead of a generated "
                "image even though tool_choice='required'. "
                "Mistral response: "
                f"{text_answer[:2500]}"
            )

        raise RuntimeError(
            "Mistral completed the request but no "
            "generated image reference was found."
        )

    reference_type = reference.get(
        "type"
    )

    reference_value = reference.get(
        "value"
    )

    if not reference_value:

        raise RuntimeError(
            "Mistral returned an empty image reference."
        )

    # ========================================================
    # DIRECT IMAGE URL
    # ========================================================

    if reference_type == "url":

        image_url = str(
            reference_value
        )

    # ========================================================
    # MISTRAL FILE ID
    # ========================================================

    elif reference_type == "file_id":

        print(
            "MISTRAL IMAGE FILE ID:",
            reference_value
        )

        image_url = (
            mistral_file_signed_url(
                reference_value,
                expiry_hours=24
            )
        )

    else:

        raise RuntimeError(
            "Unsupported Mistral image reference type: "
            f"{reference_type}"
        )

    if not image_url:

        raise RuntimeError(
            "Mistral generated the image but "
            "no usable image URL was obtained."
        )

    print("=" * 70)

    print(
        "MISTRAL IMAGE SUCCESS"
    )

    print(
        "IMAGE URL:",
        image_url
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
    """
    Mistral-only image transformation.

    Workflow:

        uploaded image
              ↓
        Mistral Vision
              ↓
        detailed visual description
              ↓
        Mistral image_generation
              ↓
        generated result
    """

    if not image_bytes:

        raise RuntimeError(
            "No source image was supplied."
        )

    print("=" * 70)

    print(
        "MISTRAL IMAGE EDIT REQUEST"
    )

    print(
        "USER INSTRUCTION:",
        prompt
    )

    print("=" * 70)

    # ========================================================
    # STEP 1 - UNDERSTAND SOURCE IMAGE
    # ========================================================

    source_description = mistral_vision(

        (
            "Describe the supplied image accurately for "
            "a visual transformation request. Include the "
            "main subject, composition, background, "
            "important objects, colors, lighting, clothing, "
            "environment and style. Do not invent details "
            "that are not visible."
        ),

        image_bytes,

        mime_type
    )

    print(
        "MISTRAL SOURCE IMAGE DESCRIPTION:"
    )

    print(
        source_description[:5000]
    )

    # ========================================================
    # STEP 2 - BUILD IMAGE TRANSFORMATION PROMPT
    # ========================================================

    transformed_prompt = f"""
Create a final image based on this original image
description and the requested modification.

ORIGINAL IMAGE DESCRIPTION:
{source_description}

USER'S REQUEST:
{prompt}

Preserve the original subject, composition, important
visual details and environment unless the user explicitly
asks to change them.

Apply the user's requested modification accurately.

Return the final visual result.
""".strip()

    # ========================================================
    # STEP 3 - GENERATE MODIFIED IMAGE
    # ========================================================

    result = mistral_generate_image(
        transformed_prompt
    )

    result["text"] = (
        "تم تعديل الصورة بنجاح."
    )

    return result


# ============================================================
# GENERATE IMAGE WITH FALLBACKS
# ============================================================
#
# There is intentionally NO alternative image provider.
#
# Mistral is the ONLY image provider.
#
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
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )

    print(
        "MIME TYPE:",
        mime_type
    )

    print(
        "IMAGE PROVIDER:",
        "MISTRAL ONLY"
    )

    print(
        "PROMPT:",
        prompt
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 70)

    try:

        if image_bytes:

            result = mistral_edit_image(

                prompt,

                image_bytes,

                mime_type
            )

        else:

            result = mistral_generate_image(
                prompt
            )

        image_url = result.get(
            "image_url"
        )

        if not image_url:

            raise RuntimeError(
                "Mistral returned no usable image URL."
            )

        return (
            "IMAGE_URL:"
            + image_url
        )

    except Exception as e:

        print("=" * 70)

        print(
            "MISTRAL IMAGE FAILED"
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

        return (
            "تعذر إنشاء أو تعديل الصورة حاليًا. "
            "حدث خطأ في خدمة الصور Mistral."
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
    """
    Main image entry point used by app.py.
    """

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
        "IMAGE PROVIDER:",
        "MISTRAL ONLY"
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
        # Explicit modification
        # ----------------------------------------------------

        if is_image_edit_request(
            message
        ):

            print(
                "IMAGE EDIT REQUEST"
            )

            try:

                result = mistral_edit_image(

                    message,

                    image_bytes,

                    mime_type
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
                        "Mistral",

                    "conversation_id":
                        conversation_id
                }

            except Exception as e:

                print(
                    "MISTRAL IMAGE EDIT FAILED:",
                    repr(e)
                )

                return {

                    "answer":
                        (
                            "تعذر تعديل الصورة حاليًا. "
                            "حدث خطأ في خدمة الصور Mistral."
                        ),

                    "imageUrl":
                        "",

                    "provider":
                        "Mistral",

                    "conversation_id":
                        conversation_id
                }


        # ----------------------------------------------------
        # Image understanding
        # ----------------------------------------------------

        print(
            "IMAGE ANALYSIS REQUEST"
        )

        try:

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

            return {

                "answer":
                    (
                        "تعذر تحليل الصورة حاليًا "
                        "باستخدام Mistral."
                    ),

                "imageUrl":
                    "",

                "provider":
                    "Mistral Vision",

                "conversation_id":
                    conversation_id
            }


    # ========================================================
    # TEXT -> IMAGE
    # ========================================================

    result = (
        generate_image_with_fallbacks(

            message,

            None,

            None,

            conversation_id
        )
    )


    # ========================================================
    # IMAGE_URL RESULT
    # ========================================================

    if (
        isinstance(
            result,
            str
        )
        and
        result.startswith(
            "IMAGE_URL:"
        )
    ):

        image_url = result[
            len("IMAGE_URL:"):
        ].strip()

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                image_url,

            "provider":
                "Mistral",

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # ERROR / TEXT RESULT
    # ========================================================

    return {

        "answer":
            str(result),

        "imageUrl":
            "",

        "provider":
            "Mistral",

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
    """
    Main application entry point.

    TEXT:
        Groq
          ↓
        OpenRouter
          ↓
        Gemini

    IMAGE:
        Mistral ONLY
    """

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
    # GREETING ONLY
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
    # TEXT PROVIDERS
    #
    # GROQ
    #   ↓
    # OPENROUTER
    #   ↓
    # GEMINI
    # ========================================================

    providers = [

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

print(
    "FINAL PROVIDER ROUTING"
)

print("-" * 70)

print(
    "TEXT:"
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
    "IMAGE ANALYSIS:"
)

print(
    "    MISTRAL ONLY"
)

print("-" * 70)

print(
    "IMAGE GENERATION:"
)

print(
    "    MISTRAL ONLY"
)

print("-" * 70)

print(
    "IMAGE EDITING:"
)

print(
    "    MISTRAL ONLY"
)

print("-" * 70)

print(
    "GROQ:"
)

print(
    "    TEXT ONLY"
)

print("-" * 70)

print(
    "OPENROUTER:"
)

print(
    "    TEXT ONLY"
)

print("-" * 70)

print(
    "GEMINI:"
)

print(
    "    TEXT ONLY"
)

print("-" * 70)

print(
    "MISTRAL:"
)

print(
    "    IMAGES ONLY"
)

print("-" * 70)

print(
    "xAI:"
)

print(
    "    DISABLED"
)

print("-" * 70)

print(
    "POLLINATIONS:"
)

print(
    "    DISABLED"
)

print("=" * 70)