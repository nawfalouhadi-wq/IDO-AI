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
#     OPENROUTER
#       ↓
#     MISTRAL
#
# IMAGE UNDERSTANDING:
#     GROQ VISION
#       ↓
#     OPENROUTER VISION
#
# IMAGE GENERATION:
#     OPENROUTER IMAGE API
#
# IMPORTANT:
#     GROQ DOES NOT GENERATE IMAGES.
#     GROQ IS USED FOR TEXT + IMAGE UNDERSTANDING.
#
# GEMINI:
#     DISABLED
#
# XAI:
#     DISABLED
#
# POLLINATIONS:
#     DISABLED
#
# ============================================================

import os
import re
import base64
import requests

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
).strip()


MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# GROQ TEXT
# ------------------------------------------------------------

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


# ------------------------------------------------------------
# GROQ VISION
# ------------------------------------------------------------

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
).strip()


# ------------------------------------------------------------
# OPENROUTER TEXT
# ------------------------------------------------------------

OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


# ------------------------------------------------------------
# OPENROUTER VISION
#
# IMPORTANT:
# This model must support image input.
# You can change it from Railway Variables.
# ------------------------------------------------------------

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "openai/gpt-4o-mini"
).strip()


# ------------------------------------------------------------
# OPENROUTER IMAGE
#
# IMPORTANT:
# This must be an image-generation model available
# through OpenRouter.
#
# Example:
#
# OPENROUTER_IMAGE_MODEL=openai/gpt-5-image
#
# You can change this from Railway Variables.
# ------------------------------------------------------------

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-5-image"
).strip()


# ------------------------------------------------------------
# MISTRAL TEXT
# ------------------------------------------------------------

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-small-latest"
).strip()


# ============================================================
# API URLS
# ============================================================

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)


MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


# ============================================================
# REQUEST TIMEOUT
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
    "READY"
    if GROQ_API_KEY
    else "MISSING"
)


print(
    "OPENROUTER CLIENT:",
    "READY"
    if OPENROUTER_API_KEY
    else "MISSING"
)


print(
    "MISTRAL CLIENT:",
    "READY"
    if MISTRAL_API_KEY
    else "MISSING"
)


print("=" * 70)

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
    "OPENROUTER VISION MODEL:",
    OPENROUTER_VISION_MODEL
)


print(
    "OPENROUTER IMAGE MODEL:",
    OPENROUTER_IMAGE_MODEL
)


print(
    "MISTRAL TEXT MODEL:",
    MISTRAL_TEXT_MODEL
)


print("=" * 70)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Aido AI.

You are the main AI assistant of the application.

IMPORTANT RULES:

1. Answer naturally and directly.

2. Understand Arabic, English and French.

3. If the user says:
   "السلام عليكم"
   and also asks a question or gives a request,
   answer the actual request.
   Do NOT respond with only a greeting.

4. If the user says ONLY:
   "السلام عليكم"
   respond naturally:
   "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك؟"

5. Never pretend that you generated an image if no image
   was actually generated.

6. Never provide fake image URLs.

7. If an image-generation request reaches the text AI by mistake,
   explain nothing about internal routing.
   The application should normally route image requests
   to the image-generation system before reaching you.

8. If an image is attached, analyze the actual image.

9. Do not treat an attached image as ordinary text.

10. Do not mention Groq, OpenRouter or Mistral unless the user
    explicitly asks which AI provider is being used.

11. Answer in the language used by the user.

12. Be concise for simple questions.

13. Be detailed when the user asks for detailed explanations.
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
    Returns True ONLY when the complete message
    is a greeting.

    Example:

        السلام عليكم
        -> True

        السلام عليكم أنشئ لي صورة
        -> False
    """

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
# GREETING RESPONSE
# ============================================================

def greeting_response():

    return (
        "وعليكم السلام ورحمة الله وبركاته، "
        "كيف يمكنني مساعدتك؟"
    )


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_KEYWORDS_AR = [

    "أنشئ صورة",
    "انشئ صورة",
    "اصنع صورة",
    "اعمل صورة",
    "اعمل لي صورة",
    "أنشئ لي صورة",
    "انشئ لي صورة",
    "اصنع لي صورة",
    "ولد صورة",
    "ولّد صورة",
    "ولد لي صورة",
    "ولّد لي صورة",
    "توليد صورة",
    "إنشاء صورة",
    "انشاء صورة",
    "صمم صورة",
    "صمم لي صورة",
    "تصميم صورة",
    "ارسم لي",
    "ارسم صورة",
    "ارسم لي صورة",
    "اعمل لي",
    "صورة لي",
    "أنشئ",
    "اصنع",
    "توليد",
    "توليد الصور",
    "إنشاء الصور",
    "تعديل الصورة",
    "عدل الصورة",
    "عدّل الصورة",
    "تحرير الصورة",
    "حرر الصورة",
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
    "generate a picture",
    "create a picture",
    "make a picture",
    "edit the image",
    "edit image",
    "modify the image",
    "modify image",
    "image generation",
    "generate photo",
    "create photo",
]


IMAGE_KEYWORDS_FR = [

    "génère une image",
    "genere une image",
    "crée une image",
    "cree une image",
    "créer une image",
    "creer une image",
    "faire une image",
    "dessine une image",
    "modifier l'image",
    "modifie l'image",
    "génération d'image",
    "generation d'image",
]


def is_image_request(message):
    """
    Detects image generation/editing requests.

    IMPORTANT:
    An ordinary message containing the word "image"
    should not automatically become an image request.
    """

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

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
    Removes common conversational prefixes while keeping
    the actual image request.
    """

    text = str(
        message or ""
    ).strip()

    if not text:

        return (
            "Create a high-quality image "
            "based on the user's request."
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

        "ولد لي صورة",

        "ولّد لي صورة",

        "ولد صورة",

        "ولّد صورة",

        "توليد صورة",

        "إنشاء صورة",

        "انشاء صورة",

        "صمم لي صورة",

        "صمم صورة",

        "ارسم لي صورة",

        "ارسم صورة",

        "generate an image",

        "generate image",

        "create an image",

        "create image",

        "make an image",

        "make image",

        "draw an image",

        "draw image",

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
# HTTP POST HELPER
# ============================================================

def safe_post(
    url,
    headers=None,
    json_data=None,
    timeout=REQUEST_TIMEOUT
):

    response = requests.post(

        url,

        headers=headers or {},

        json=json_data,

        timeout=timeout
    )

    return response


# ============================================================
# EXTRACT OPENAI-COMPATIBLE TEXT
# ============================================================

def extract_text_response(data):

    if not isinstance(
        data,
        dict
    ):

        return ""


    choices = data.get(
        "choices"
    )


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

            f"Groq HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )


    answer = extract_text_response(
        response.json()
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


    if not image_bytes:

        raise RuntimeError(
            "No image bytes were provided."
        )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    image_url = (

        f"data:"
        f"{mime_type or 'image/jpeg'}"
        f";base64,"
        f"{encoded}"
    )


    headers = {

        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json",
    }


    vision_prompt = """

You are analyzing an image for Aido AI.

Look carefully at the attached image.

Answer the user's question about the image.

If the user asks what is in the image,
describe the important visible elements.

If there is text in the image,
read it when possible.

Do not pretend to see something that is not visible.

Answer naturally in the user's language.

"""


    payload = {

        "model":
            GROQ_VISION_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    vision_prompt,
            },

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            message or
                            "حلل هذه الصورة."
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
            f"{response.text[:1000]}"
        )


    answer = extract_text_response(
        response.json()
    )


    if not answer:

        raise RuntimeError(
            "Groq Vision returned empty response."
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

        OPENROUTER_CHAT_URL,

        headers=headers,

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(

            f"OpenRouter HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
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


    if not image_bytes:

        raise RuntimeError(
            "No image bytes were provided."
        )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    image_url = (

        f"data:"
        f"{mime_type or 'image/jpeg'}"
        f";base64,"
        f"{encoded}"
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
            OPENROUTER_VISION_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    (
                        "Analyze the attached image carefully. "
                        "Answer naturally in the user's language. "
                        "Do not invent visual details."
                    ),
            },

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            message or
                            "حلل هذه الصورة."
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

        OPENROUTER_CHAT_URL,

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
            f"{response.text[:1000]}"
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


    # ========================================================
    # IMAGE GENERATION
    # ========================================================
    #
    # OpenRouter now provides a dedicated /images endpoint.
    #
    # ========================================================

    payload = {

        "model":
            OPENROUTER_IMAGE_MODEL,

        "prompt":
            prompt,

        "n":
            1,

        "size":
            "1024x1024",
    }


    # ========================================================
    # OPTIONAL REFERENCE IMAGE
    # ========================================================
    #
    # If the user uploaded an image and asked for editing,
    # send it as an input reference when supported.
    #
    # ========================================================

    if image_bytes:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )


        payload["input_references"] = [

            {
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
            }

        ]


    response = safe_post(

        OPENROUTER_IMAGE_URL,

        headers=headers,

        json_data=payload
    )


    if response.status_code >= 400:

        raise RuntimeError(

            f"OpenRouter Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )


    data = response.json()


    images = data.get(
        "data",
        []
    )


    if not images:

        raise RuntimeError(
            "OpenRouter Image returned no image data."
        )


    first = images[0]


    # ========================================================
    # BASE64 IMAGE
    # ========================================================

    b64 = first.get(
        "b64_json"
    )


    if b64:

        media_type = first.get(
            "media_type",
            "image/png"
        )


        return {

            "image_url":
                (
                    f"data:"
                    f"{media_type}"
                    f";base64,"
                    f"{b64}"
                ),

            "text":
                "تم إنشاء الصورة بنجاح.",

            "provider":
                "OpenRouter",

            "model":
                OPENROUTER_IMAGE_MODEL,
        }


    # ========================================================
    # SOME MODELS / RESPONSES MAY RETURN URL
    # ========================================================

    image_url = first.get(
        "url"
    )


    if image_url:

        return {

            "image_url":
                image_url,

            "text":
                "تم إنشاء الصورة بنجاح.",

            "provider":
                "OpenRouter",

            "model":
                OPENROUTER_IMAGE_MODEL,
        }


    raise RuntimeError(
        "OpenRouter returned image data "
        "without b64_json or URL."
    )


# ============================================================
# IMAGE GENERATION
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
        "HAS REFERENCE IMAGE:",
        bool(image_bytes)
    )

    print("=" * 70)


    # ========================================================
    # ONLY IMAGE GENERATOR:
    #
    # OPENROUTER
    #
    # Groq cannot generate images.
    # ========================================================

    try:

        print(
            "TRYING IMAGE PROVIDER: OpenRouter"
        )


        result = openrouter_generate_image(

            prompt,

            image_bytes,

            mime_type
        )


        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(
                "Invalid OpenRouter image response."
            )


        image_url = result.get(
            "image_url"
        )


        if not image_url:

            raise RuntimeError(
                "OpenRouter returned no image."
            )


        print(
            "IMAGE GENERATION SUCCESS: OpenRouter"
        )


        return {

            "answer":
                result.get(
                    "text",
                    "تم إنشاء الصورة بنجاح."
                ),

            "imageUrl":
                image_url,

            "provider":
                "OpenRouter",

            "conversation_id":
                conversation_id,
        }


    except Exception as e:

        print(
            "OPENROUTER IMAGE FAILED:",
            repr(e)
        )


    # ========================================================
    # FAILED
    # ========================================================

    print("=" * 70)

    print(
        "IMAGE GENERATION FAILED"
    )

    print("=" * 70)


    return {

        "answer":
            (
                "تعذر إنشاء الصورة حاليًا. "
                "مولد الصور المستخدم هو OpenRouter، "
                "ولم يُرجع صورة."
            ),

        "imageUrl":
            "",

        "provider":
            None,

        "conversation_id":
            conversation_id,
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
                conversation_id,
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
                conversation_id,
        }


    # ========================================================
    # IMAGE REQUEST
    #
    # IMPORTANT:
    #
    # Never send:
    #
    # "أنشئ لي صورة..."
    #
    # to Groq text.
    #
    # ========================================================

    if is_image_request(
        message
    ):

        print(
            "IMAGE REQUEST DETECTED"
        )


        return generate_image_with_fallbacks(

            message,

            None,

            None,

            conversation_id
        )


    # ========================================================
    # TEXT AI ROUTE
    #
    # GROQ
    #   ↓
    # OPENROUTER
    #   ↓
    # MISTRAL
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
            "Mistral",
            mistral_text
        ),

    ]


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

            print(
                "TEXT PROVIDER FAILED:",
                provider_name,
                repr(e)
            )


    # ========================================================
    # ALL TEXT PROVIDERS FAILED
    # ========================================================

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
# GET IMAGE RESPONSE
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

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
    # CASE 1:
    # IMAGE WAS UPLOADED
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # USER WANTS TO EDIT / TRANSFORM THE IMAGE
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

                mime_type,

                conversation_id
            )


        # ----------------------------------------------------
        # USER WANTS TO UNDERSTAND THE IMAGE
        #
        # GROQ VISION
        #       ↓
        # OPENROUTER VISION
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


        # ----------------------------------------------------
        # ALL VISION PROVIDERS FAILED
        # ----------------------------------------------------

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
    # TEXT REQUEST FOR IMAGE
    # ========================================================

    return generate_image_with_fallbacks(

        message,

        None,

        None,

        conversation_id
    )


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message
):

    """
    Compatibility function.

    Older app.py/API.py versions may call:

        quick_response(message)
    """

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
    "    GROQ -> OPENROUTER -> MISTRAL"
)


print(
    "VISION ROUTE:"
)

print(
    "    GROQ VISION -> OPENROUTER VISION"
)


print(
    "IMAGE GENERATION:"
)

print(
    "    OPENROUTER IMAGE API"
)


print(
    "GEMINI:"
)

print(
    "    DISABLED"
)


print(
    "XAI:"
)

print(
    "    DISABLED"
)


print(
    "POLLINATIONS:"
)

print(
    "    DISABLED"
)


print(
    "SMART GREETING:"
)

print(
    "    ENABLED"
)


print(
    "IMAGE REQUEST ROUTING:"
)

print(
    "    ENABLED"
)


print("=" * 70)