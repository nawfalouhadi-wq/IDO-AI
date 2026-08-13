# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# PROVIDERS USED:
#
# TEXT:
#     GROQ
#       ↓
#     OPENROUTER
#
# VISION:
#     GROQ VISION
#       ↓
#     OPENROUTER VISION
#
# IMAGE GENERATION / EDITING:
#     OPENROUTER
#
# IMPORTANT:
#     No direct Gemini API
#     No Mistral
#     No xAI
#     No Pollinations
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


# ============================================================
# MODELS
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
# OPENROUTER IMAGE
#
# Current image model available through OpenRouter.
# ------------------------------------------------------------

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "google/gemini-3.1-flash-image"
).strip()


# ============================================================
# URLS
# ============================================================

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
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
    "OPENROUTER CLIENT:",
    "READY" if OPENROUTER_API_KEY else "MISSING"
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
    "OPENROUTER IMAGE MODEL:",
    OPENROUTER_IMAGE_MODEL
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

3. If the user says:
   "السلام عليكم"
   and also asks a question,
   answer the question normally.

4. If the user only says:
   "السلام عليكم"

   respond:

   "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك؟"

5. Never pretend to generate an image as text.

6. Image generation is handled by the application image system.

7. If the user asks to generate or edit an image,
   the application will route the request to the image generator.

8. Do not mention internal provider routing unless the user asks.

9. Be concise for simple questions.

10. Be detailed when the user asks for explanations.

11. Answer in the language used by the user whenever possible.
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
    Returns True only when the entire message
    is a greeting.
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

    "أنشئ صورة",
    "انشئ صورة",
    "اصنع صورة",
    "اعمل صورة",
    "اعمل لي صورة",

    "أنشئ لي صورة",
    "انشئ لي صورة",
    "اصنع لي صورة",

    "ولّد صورة",
    "ولد صورة",

    "توليد صورة",
    "إنشاء صورة",

    "ارسم",
    "ارسم لي",

    "صمم صورة",
    "تصميم صورة",

    "صورة",
    "صور",

    "عدّل الصورة",
    "عدل الصورة",

    "تعديل الصورة",
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

    "edit the image",
    "edit image",

    "modify the image",
    "modify image",

    "image generation",

    "generate a picture",
    "create a picture",

    "generate a photo",
    "create a photo",
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
    Detect image generation or editing requests.
    """

    if not message:
        return False

    text = str(message).strip().lower()

    # Arabic
    for keyword in IMAGE_KEYWORDS_AR:

        if keyword.lower() in text:
            return True

    # English
    for keyword in IMAGE_KEYWORDS_EN:

        if keyword.lower() in text:
            return True

    # French
    for keyword in IMAGE_KEYWORDS_FR:

        if keyword.lower() in text:
            return True

    return False


# ============================================================
# CLEAN IMAGE PROMPT
# ============================================================

def clean_image_prompt(message):
    """
    Removes common conversational prefixes
    while preserving the actual image request.
    """

    text = str(
        message or ""
    ).strip()

    if not text:

        return (
            "Create a high-quality professional image."
        )

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
# SAFE POST
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
            "Groq HTTP "
            f"{response.status_code}: "
            f"{response.text[:700]}"
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
            "OpenRouter HTTP "
            f"{response.status_code}: "
            f"{response.text[:700]}"
        )

    data = response.json()

    answer = extract_text_response(
        data
    )

    if not answer:

        raise RuntimeError(
            "OpenRouter returned an empty response."
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
                        }
                    }
                ],
            }
        ],

        "temperature":
            0.4,

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
            "Groq Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:700]}"
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
                ],
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
            "OpenRouter Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:700]}"
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
# EXTRACT IMAGE FROM OPENROUTER RESPONSE
# ============================================================

def extract_openrouter_image(data):

    if not isinstance(
        data,
        dict
    ):
        return None

    choices = data.get(
        "choices",
        []
    )

    if not choices:
        return None

    message = choices[0].get(
        "message",
        {}
    )

    # --------------------------------------------------------
    # Current OpenRouter image response:
    #
    # message.images
    # --------------------------------------------------------

    images = message.get(
        "images"
    )

    if isinstance(
        images,
        list
    ):

        for image in images:

            if not isinstance(
                image,
                dict
            ):
                continue

            image_url = image.get(
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

                    return url

    # --------------------------------------------------------
    # Some responses can expose image objects
    # inside content.
    # --------------------------------------------------------

    content = message.get(
        "content"
    )

    if isinstance(
        content,
        list
    ):

        for item in content:

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

                    return url

            image = item.get(
                "image"
            )

            if isinstance(
                image,
                dict
            ):

                image_url = image.get(
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

                        return url

    return None


# ============================================================
# OPENROUTER IMAGE GENERATION / EDITING
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
            "OPENROUTER_IMAGE_MODEL is missing."
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

    # --------------------------------------------------------
    # TEXT ONLY
    # --------------------------------------------------------

    if not image_bytes:

        user_content = prompt

    # --------------------------------------------------------
    # IMAGE EDITING
    # --------------------------------------------------------

    else:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:{mime_type or 'image/jpeg'}"
            f";base64,{encoded}"
        )

        user_content = [

            {
                "type":
                    "text",

                "text":
                    (
                        "Edit the supplied image according "
                        "to this instruction. Return the "
                        "edited image.\n\n"
                        f"INSTRUCTION:\n{prompt}"
                    ),
            },

            {
                "type":
                    "image_url",

                "image_url": {

                    "url":
                        image_url
                },
            }
        ]

    payload = {

        "model":
            OPENROUTER_IMAGE_MODEL,

        "messages": [

            {
                "role":
                    "user",

                "content":
                    user_content,
            }
        ],

        # ----------------------------------------------------
        # VERY IMPORTANT:
        #
        # OpenRouter image models use image + text modalities.
        # ----------------------------------------------------

        "modalities": [
            "image",
            "text"
        ],

        "temperature":
            0.7,
    }

    print("=" * 70)

    print(
        "OPENROUTER IMAGE REQUEST"
    )

    print(
        "IMAGE MODEL:",
        OPENROUTER_IMAGE_MODEL
    )

    print(
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 70)

    response = safe_post(

        OPENROUTER_URL,

        headers=headers,

        json_data=payload,

        timeout=REQUEST_TIMEOUT
    )

    # --------------------------------------------------------
    # HTTP ERROR
    # --------------------------------------------------------

    if response.status_code >= 400:

        raise RuntimeError(
            "OpenRouter Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            "OpenRouter returned invalid JSON: "
            f"{e}"
        )

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image_url = extract_openrouter_image(
        data
    )

    if image_url:

        print(
            "OPENROUTER IMAGE SUCCESS"
        )

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

    # --------------------------------------------------------
    # Debug response when no image was found
    # --------------------------------------------------------

    print(
        "OPENROUTER IMAGE RESPONSE:"
    )

    print(
        str(data)[:5000]
    )

    raise RuntimeError(
        "OpenRouter completed the request "
        "but returned no image data."
    )


# ============================================================
# IMAGE GENERATION FALLBACK
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

    print("=" * 70)

    # --------------------------------------------------------
    # ONLY IMAGE PROVIDER:
    #
    # OPENROUTER
    # --------------------------------------------------------

    try:

        result = openrouter_generate_image(

            prompt,

            image_bytes,

            mime_type
        )

        image_url = result.get(
            "image_url"
        )

        if not image_url:

            raise RuntimeError(
                "OpenRouter returned no image URL."
            )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # app.py currently expects:
        #
        # IMAGE_URL:<url>
        #
        # Therefore return exactly that format.
        # ----------------------------------------------------

        return (
            "IMAGE_URL:"
            + image_url
        )

    except Exception as e:

        print("=" * 70)

        print(
            "OPENROUTER IMAGE FAILED:"
        )

        print(
            repr(e)
        )

        print("=" * 70)

        return (
            "تعذر إنشاء الصورة حاليًا. "
            "حدث خطأ في خدمة توليد الصور."
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
    # IMAGE UPLOADED
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # Explicit image edit/generation request
        # ----------------------------------------------------

        if is_image_request(
            message
        ):

            print(
                "IMAGE EDIT REQUEST"
            )

            return generate_image_with_fallbacks(

                message,

                image_bytes,

                mime_type,

                conversation_id
            )

        # ----------------------------------------------------
        # IMAGE UNDERSTANDING
        #
        # Groq Vision
        #      ↓
        # OpenRouter Vision
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

        for (
            provider_name,
            provider_function
        ) in vision_providers:

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
                "تعذر تحليل الصورة حاليًا.",

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id,
        }

    # ========================================================
    # TEXT -> IMAGE
    # ========================================================

    return generate_image_with_fallbacks(

        message,

        None,

        None,

        conversation_id
    )


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
                conversation_id,
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

        result = get_image_response(

            message,

            None,

            None,

            conversation_id
        )

        # ----------------------------------------------------
        # app.py expects IMAGE_URL:
        # ----------------------------------------------------

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
                        "OpenRouter",

                    "conversation_id":
                        conversation_id,
                }

            return {

                "answer":
                    result,

                "imageUrl":
                    "",

                "provider":
                    "OpenRouter",

                "conversation_id":
                    conversation_id,
            }

        return result

    # ========================================================
    # TEXT PROVIDERS
    #
    # GROQ
    #   ↓
    # OPENROUTER
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
                        conversation_id,
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
    # EVERYTHING FAILED
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
    "PRIMARY TEXT AI:"
)

print(
    "    GROQ"
)

print(
    "TEXT ROUTE:"
)

print(
    "    GROQ -> OPENROUTER"
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
    "    OPENROUTER IMAGE"
)

print(
    "OPENROUTER IMAGE MODEL:"
)

print(
    f"    {OPENROUTER_IMAGE_MODEL}"
)

print(
    "DIRECT GEMINI API:"
)

print(
    "    DISABLED"
)

print(
    "MISTRAL:"
)

print(
    "    DISABLED"
)

print(
    "xAI:"
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

print("=" * 70)