# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# ARCHITECTURE
#
# PRIMARY TEXT AI:
#     GROQ
#
# PRIMARY IMAGE UNDERSTANDING:
#     GROQ VISION
#
# IMAGE UNDERSTANDING FALLBACK:
#     OPENROUTER VISION
#
# IMAGE GENERATION:
#     OPENROUTER IMAGE API
#
# IMPORTANT:
#     Groq does NOT generate images.
#     Therefore image-generation requests NEVER go to Groq
#     as normal text requests.
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
# OPENROUTER TEXT / VISION
# ------------------------------------------------------------
#
# IMPORTANT:
# This model MUST support image input when used for vision.
#
# You can change it from Railway Variables.
#

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "meta-llama/llama-4-maverick"
).strip()


# ------------------------------------------------------------
# OPENROUTER IMAGE
# ------------------------------------------------------------
#
# OpenRouter now has a dedicated /images endpoint.
#
# Default:
# Grok Imagine through OpenRouter.
#
# You can replace this in Railway Variables with another
# OpenRouter image-generation model.
#

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "x-ai/grok-imagine-image-quality"
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
    "OPENROUTER VISION MODEL:",
    OPENROUTER_VISION_MODEL
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

You are the main AI assistant of the application.

IMPORTANT RULES:

1. Answer naturally and directly.

2. Understand Arabic, English and French.

3. If the user says:
   "السلام عليكم"
   and also asks a question or gives a request,
   answer the actual request.
   Do NOT return only a greeting.

4. If the user says only:
   "السلام عليكم"
   respond naturally with:
   "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك؟"

5. Never pretend that you generated an image if no image
   was actually generated.

6. Image-generation requests are handled by the application's
   image-generation system.

7. Never answer an image-generation request as if it were
   an ordinary text question.

8. If the user asks to create, generate, draw, make or edit
   an image, the application will route the request to the
   image-generation system.

9. If the user uploads an image and asks a question about it,
   analyze the actual uploaded image.

10. Do not invent API failures.

11. Do not mention internal provider routing unless the user
    explicitly asks about it.

12. Be concise for simple questions.

13. Be detailed when the user asks for an explanation.

14. If the user asks for code, provide real code in the
    requested programming language.

15. Never claim that you cannot see an uploaded image when
    the image was actually provided to the vision system.
"""


# ============================================================
# GREETING DETECTION
# ============================================================

GREETING_ONLY_PATTERNS = [

    r"^\s*السلام عليكم\s*[.!؟،]*\s*$",

    r"^\s*السلام عليكم ورحمة الله وبركاته\s*[.!؟،]*\s*$",

    r"^\s*سلام عليكم\s*[.!؟،]*\s*$",

    r"^\s*السلام\s*[.!؟،]*\s*$",
]


def is_greeting_only(message):
    """
    Return True only when the complete message is a greeting.

    Examples:

        السلام عليكم
            -> True

        السلام عليكم أريد صورة لسيارة
            -> False

        السلام عليكم كيف حالك؟
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

    "أنشئ لي صورة",
    "انشئ لي صورة",

    "اصنع لي صورة",
    "اعمل لي صورة",

    "ولد صورة",
    "ولّد صورة",

    "توليد صورة",
    "إنشاء صورة",

    "صمم صورة",
    "تصميم صورة",

    "ارسم صورة",
    "ارسم لي صورة",

    "ارسم لي",

    "صورة",
    "صور",

    "الصورة",
    "الصور",

    "أنشئ",
    "اصنع",

    "ولّد",
    "ولد",

    "عدّل الصورة",
    "عدل الصورة",

    "تعديل الصورة",
    "تحرير الصورة",

    "حرر الصورة",

    "غيّر الصورة",
    "غير الصورة",

    "حسّن الصورة",
    "حسن الصورة",
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

    "create a picture",
    "generate a picture",

    "make a picture",

    "edit the image",
    "edit image",

    "modify the image",
    "modify image",

    "edit the picture",
    "modify the picture",

    "image generation",

    "generate a photo",
    "create a photo",

    "picture",
    "photo",
    "image",
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

    "créer une image",
    "creer une image",

    "image",
    "photo",
]


def is_image_request(message):
    """
    Detect image generation/editing requests.

    IMPORTANT:
    This function is checked BEFORE the normal text AI.
    Therefore Groq will not answer an image request as text.
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
    Prepare the user's request for the image generator.
    """

    text = str(
        message or ""
    ).strip()

    if not text:

        return (
            "Create a high-quality image "
            "based on the user's request."
        )

    # --------------------------------------------------------
    # Remove conversational prefixes
    # --------------------------------------------------------

    prefixes = [

        "أنشئ لي صورة",
        "انشئ لي صورة",

        "اصنع لي صورة",
        "اعمل لي صورة",

        "أنشئ صورة",
        "انشئ صورة",

        "اصنع صورة",
        "اعمل صورة",

        "ولد صورة",
        "ولّد صورة",

        "أنشئ",
        "انشئ",

        "اصنع",
        "اعمل",

        "ولّد",
        "ولد",

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

        "create a picture",
        "generate a picture",
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
# EXTRACT TEXT FROM OPENAI-COMPATIBLE RESPONSE
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

    if not isinstance(
        first,
        dict
    ):

        return ""

    message = first.get(
        "message",
        {}
    )

    if not isinstance(
        message,
        dict
    ):

        return ""

    content = message.get(
        "content"
    )

    # --------------------------------------------------------
    # Simple string
    # --------------------------------------------------------

    if isinstance(
        content,
        str
    ):

        return content.strip()

    # --------------------------------------------------------
    # Content array
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # IMPORTANT:
    # Show real provider error in Railway logs.
    # --------------------------------------------------------

    if response.status_code >= 400:

        raise RuntimeError(
            "Groq HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "Groq returned invalid JSON: "
            f"{response.text[:1000]}"
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
# GROQ VISION
# ============================================================

def groq_vision(
    message,
    image_bytes,
    mime_type
):
    """
    Analyze a real uploaded image using Groq Vision.
    """

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )

    if not image_bytes:

        raise RuntimeError(
            "No image bytes were provided."
        )

    # --------------------------------------------------------
    # Encode uploaded image
    # --------------------------------------------------------

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )

    safe_mime_type = (
        mime_type
        or
        "image/jpeg"
    )

    image_url = (
        f"data:{safe_mime_type};base64,"
        f"{encoded}"
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
                            (
                                message
                                or
                                "حلل هذه الصورة بالتفصيل."
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
                ],
            }
        ],

        "temperature":
            0.4,

        "max_tokens":
            4096,
    }

    print(
        "GROQ VISION REQUEST:"
    )

    print(
        "MODEL:",
        GROQ_VISION_MODEL
    )

    print(
        "MIME:",
        safe_mime_type
    )

    print(
        "IMAGE BYTES:",
        len(image_bytes)
    )

    response = safe_post(

        GROQ_URL,

        headers=headers,

        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "Groq Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "Groq Vision returned invalid JSON: "
            f"{response.text[:1500]}"
        )

    answer = extract_text_response(
        data
    )

    if not answer:

        raise RuntimeError(
            "Groq Vision returned empty text."
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
    """
    Backup image-understanding provider.

    OpenRouter requires a vision-capable model when an
    image_url is included.
    """

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

    safe_mime_type = (
        mime_type
        or
        "image/jpeg"
    )

    image_url = (
        f"data:{safe_mime_type};base64,"
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
                            (
                                message
                                or
                                "حلل هذه الصورة."
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
                ],
            }
        ],

        "max_tokens":
            4096,

        "temperature":
            0.4,
    }

    print(
        "OPENROUTER VISION REQUEST:"
    )

    print(
        "MODEL:",
        OPENROUTER_VISION_MODEL
    )

    response = safe_post(

        OPENROUTER_CHAT_URL,

        headers=headers,

        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "OpenRouter Vision HTTP "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "OpenRouter Vision returned invalid JSON: "
            f"{response.text[:1500]}"
        )

    answer = extract_text_response(
        data
    )

    if not answer:

        raise RuntimeError(
            "OpenRouter Vision returned empty text."
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
    """
    Generate or edit an image using OpenRouter's dedicated
    Image API.

    Endpoint:
        POST /api/v1/images

    The API returns base64 image data.
    """

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

    payload = {

        "model":
            OPENROUTER_IMAGE_MODEL,

        "prompt":
            prompt,

        "n":
            1,

        "resolution":
            "1K",

        "aspect_ratio":
            "1:1",
    }

    # --------------------------------------------------------
    # IMAGE EDITING / REFERENCE IMAGE
    # --------------------------------------------------------
    #
    # If the user uploaded an image, provide it as an
    # input reference when supported by the selected model.
    #

    if image_bytes:

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        safe_mime_type = (
            mime_type
            or
            "image/jpeg"
        )

        reference_data_url = (
            f"data:{safe_mime_type};base64,"
            f"{encoded}"
        )

        payload[
            "input_references"
        ] = [

            reference_data_url
        ]

    print(
        "OPENROUTER IMAGE REQUEST:"
    )

    print(
        "MODEL:",
        OPENROUTER_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        prompt
    )

    print(
        "HAS REFERENCE IMAGE:",
        bool(image_bytes)
    )

    response = safe_post(

        OPENROUTER_IMAGE_URL,

        headers=headers,

        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            "OpenRouter Image HTTP "
            f"{response.status_code}: "
            f"{response.text[:2000]}"
        )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "OpenRouter Image returned invalid JSON: "
            f"{response.text[:2000]}"
        )

    images = data.get(
        "data",
        []
    )

    if not images:

        raise RuntimeError(
            "OpenRouter Image returned no images."
        )

    # --------------------------------------------------------
    # Find first valid image
    # --------------------------------------------------------

    for image in images:

        if not isinstance(
            image,
            dict
        ):

            continue

        b64_json = image.get(
            "b64_json"
        )

        if b64_json:

            media_type = image.get(
                "media_type",
                "image/png"
            )

            data_url = (
                f"data:{media_type};base64,"
                f"{b64_json}"
            )

            return {

                "image_url":
                    data_url,

                "text":
                    "تم إنشاء الصورة بنجاح.",

                "provider":
                    "OpenRouter",

                "model":
                    OPENROUTER_IMAGE_MODEL,
            }

        # ----------------------------------------------------
        # Some compatible responses may provide a URL.
        # ----------------------------------------------------

        url = image.get(
            "url"
        )

        if url:

            return {

                "image_url":
                    url,

                "text":
                    "تم إنشاء الصورة بنجاح.",

                "provider":
                    "OpenRouter",

                "model":
                    OPENROUTER_IMAGE_MODEL,
            }

    raise RuntimeError(
        "OpenRouter returned image entries "
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
    """
    Image generation route.

    IMPORTANT:
        Only OpenRouter is used for image generation.

    Groq is NOT called here because Groq is the text/vision
    provider, not the image-generation provider.
    """

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

    try:

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
                "OpenRouter returned no image data."
            )

        print(
            "=" * 70
        )

        print(
            "IMAGE GENERATION SUCCESS"
        )

        print(
            "PROVIDER:",
            result.get(
                "provider"
            )
        )

        print(
            "MODEL:",
            result.get(
                "model"
            )
        )

        print(
            "IMAGE DATA:",
            "DATA URL"
            if image_url.startswith(
                "data:"
            )
            else "REMOTE URL"
        )

        print(
            "=" * 70
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
                result.get(
                    "provider",
                    "OpenRouter"
                ),

            "conversation_id":
                conversation_id,
        }

    except Exception as e:

        print(
            "=" * 70
        )

        print(
            "OPENROUTER IMAGE GENERATION FAILED:"
        )

        print(
            repr(e)
        )

        print(
            "=" * 70
        )

        return {

            "answer":
                (
                    "تعذر إنشاء الصورة حاليًا. "
                    "حدث خطأ في خدمة توليد الصور."
                ),

            "imageUrl":
                "",

            "provider":
                None,

            "conversation_id":
                conversation_id,

            "error":
                str(e),
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
    """
    Main image entry point.

    CASE A:
        Uploaded image + normal question
        -> Groq Vision
        -> OpenRouter Vision fallback

    CASE B:
        Uploaded image + edit/generate request
        -> OpenRouter Image

    CASE C:
        No image + generation request
        -> OpenRouter Image
    """

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
    # CASE A/B:
    # User uploaded an image
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # Image editing request
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
        # Image understanding
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

        errors = []

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

                error_text = (
                    f"{provider_name}: "
                    f"{repr(e)}"
                )

                errors.append(
                    error_text
                )

                print(
                    "VISION PROVIDER FAILED:",
                    error_text
                )

        # ----------------------------------------------------
        # All vision providers failed
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

            "error":
                " | ".join(
                    errors
                ),
        }

    # ========================================================
    # CASE C:
    # Text-only image generation
    # ========================================================

    return generate_image_with_fallbacks(

        message,

        None,

        None,

        conversation_id
    )


# ============================================================
# MAIN TEXT RESPONSE
# ============================================================

def get_response(
    message,
    conversation_id=None
):
    """
    Main brain entry point used by app.py/API.py.
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
    # ========================================================
    #
    # VERY IMPORTANT:
    #
    # Check this BEFORE Groq.
    #
    # This prevents:
    #
    # User:
    #     "أنشئ لي صورة لسيارة"
    #
    # from becoming:
    #
    #     Groq -> "إليك وصفًا للصورة..."
    #
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
    # PRIMARY TEXT AI
    # ========================================================

    try:

        print(
            "TRYING PRIMARY TEXT PROVIDER: GROQ"
        )

        answer = groq_text(
            message
        )

        if answer:

            print(
                "TEXT PROVIDER SUCCESS: GROQ"
            )

            return {

                "answer":
                    answer,

                "imageUrl":
                    "",

                "provider":
                    "Groq",

                "conversation_id":
                    conversation_id,
            }

    except Exception as e:

        print(
            "=" * 70
        )

        print(
            "GROQ TEXT FAILED:"
        )

        print(
            repr(e)
        )

        print(
            "=" * 70
        )

    # ========================================================
    # NO SECONDARY TEXT AI
    # ========================================================
    #
    # According to the requested architecture:
    #
    # Groq is the main brain.
    #
    # OpenRouter is used for image/vision fallback.
    #
    # We do not silently route normal text to Gemini,
    # Mistral, xAI or Pollinations.
    #
    # ========================================================

    return {

        "answer":
            (
                "تعذر الحصول على إجابة من Groq حاليًا. "
                "تحقق من GROQ_API_KEY أو إعدادات نموذج Groq."
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

    Older app.py versions may call:

        quick_response(message)
    """

    result = get_response(
        message
    )

    if isinstance(
        result,
        dict
    ):

        return result.get(
            "answer",
            ""
        )

    return str(
        result or ""
    )


# ============================================================
# SIMPLE ASK FUNCTION
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
    "TEXT:"
)

print(
    "    GROQ ONLY"
)

print(
    "VISION:"
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
    "MISTRAL:"
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
    "GREETING:"
)

print(
    "    SMART GREETING DETECTION ENABLED"
)

print("=" * 70)