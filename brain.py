# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
# FINAL ROUTING
#
# TEXT:
#   XAI
#     ↓
#   MISTRAL
#     ↓
#   GROQ
#     ↓
#   OPENROUTER
#     ↓
#   GEMINI
#
# IMAGE UNDERSTANDING:
#   XAI VISION
#     ↓
#   MISTRAL VISION
#
# IMAGE GENERATION:
#   XAI IMAGE
#     ↓
#   GROQ IMAGE (if available)
#     ↓
#   MISTRAL IMAGE
#
# IMAGE EDITING:
#   XAI IMAGE EDIT
#     ↓
#   GROQ IMAGE EDIT (if available)
#     ↓
#   MISTRAL IMAGE EDIT
#
# IMPORTANT:
# - XAI uses XAI_API_KEY
# - MISTRAL uses MISTRAL_API_KEY
# - GROQ is a fallback, not the primary image provider
# ============================================================

import os
import time
import base64
import mimetypes
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "180"))

# ------------------------------------------------------------
# API KEYS
# ------------------------------------------------------------

XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# ------------------------------------------------------------
# MODELS
# ------------------------------------------------------------

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash"
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
)

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
)

XAI_TEXT_MODEL = os.getenv(
    "XAI_TEXT_MODEL",
    "grok-4.5"
)

XAI_VISION_MODEL = os.getenv(
    "XAI_VISION_MODEL",
    "grok-4.5"
)

XAI_IMAGE_MODEL = os.getenv(
    "XAI_IMAGE_MODEL",
    "grok-imagine-image-quality"
)

# ------------------------------------------------------------
# MISTRAL RETRIES
# ------------------------------------------------------------

MISTRAL_MAX_RETRIES = int(
    os.getenv("MISTRAL_MAX_RETRIES", "2")
)

MISTRAL_RETRY_BASE_SECONDS = float(
    os.getenv("MISTRAL_RETRY_BASE_SECONDS", "2")
)

# ============================================================
# CLIENTS
# ============================================================

xai_client = None
mistral_client = None
groq_client = None
openrouter_client = None
gemini_client = None

# ------------------------------------------------------------
# xAI
# ------------------------------------------------------------

if XAI_API_KEY:
    try:
        from openai import OpenAI

        xai_client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            timeout=AI_REQUEST_TIMEOUT
        )

        print("XAI CLIENT: READY")

    except Exception as e:
        print("XAI CLIENT: ERROR:", e)

else:
    print("XAI CLIENT: NOT CONFIGURED")

# ------------------------------------------------------------
# Mistral
# ------------------------------------------------------------

if MISTRAL_API_KEY:
    try:
        from mistralai import Mistral

        mistral_client = Mistral(
            api_key=MISTRAL_API_KEY
        )

        print("MISTRAL CLIENT: READY")

    except Exception as e:
        print("MISTRAL CLIENT: ERROR:", e)

else:
    print("MISTRAL CLIENT: NOT CONFIGURED")

# ------------------------------------------------------------
# Groq
# ------------------------------------------------------------

if GROQ_API_KEY:
    try:
        from groq import Groq

        groq_client = Groq(
            api_key=GROQ_API_KEY
        )

        print("GROQ CLIENT: READY")

    except Exception as e:
        print("GROQ CLIENT: ERROR:", e)

else:
    print("GROQ CLIENT: NOT CONFIGURED")

# ------------------------------------------------------------
# OpenRouter
# ------------------------------------------------------------

if OPENROUTER_API_KEY:
    try:
        from openai import OpenAI

        openrouter_client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=AI_REQUEST_TIMEOUT
        )

        print("OPENROUTER CLIENT: READY")

    except Exception as e:
        print("OPENROUTER CLIENT: ERROR:", e)

else:
    print("OPENROUTER CLIENT: NOT CONFIGURED")

# ------------------------------------------------------------
# Gemini
# ------------------------------------------------------------

if GEMINI_API_KEY:
    try:
        from google import genai

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print("GEMINI CLIENT: READY")

    except Exception as e:
        print("GEMINI CLIENT: ERROR:", e)

else:
    print("GEMINI CLIENT: NOT CONFIGURED")


# ============================================================
# STARTUP INFORMATION
# ============================================================

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)

print("XAI TEXT MODEL:", XAI_TEXT_MODEL)
print("XAI VISION MODEL:", XAI_VISION_MODEL)
print("XAI IMAGE MODEL:", XAI_IMAGE_MODEL)

print("MISTRAL VISION MODEL:", MISTRAL_VISION_MODEL)
print("MISTRAL IMAGE MODEL:", MISTRAL_IMAGE_MODEL)

print("GROQ TEXT MODEL:", GROQ_TEXT_MODEL)

print("OPENROUTER TEXT MODEL:", OPENROUTER_TEXT_MODEL)

print("GEMINI TEXT MODEL:", GEMINI_TEXT_MODEL)

print("MISTRAL MAX RETRIES:", MISTRAL_MAX_RETRIES)
print(
    "MISTRAL RETRY BASE SECONDS:",
    MISTRAL_RETRY_BASE_SECONDS
)

print("AI REQUEST TIMEOUT:", AI_REQUEST_TIMEOUT)

print("=" * 70)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are IDO AI, a powerful multilingual AI assistant.

You can communicate in Arabic, Moroccan Arabic,
English, French and other languages.

Always answer the user's actual question.

Do not claim that you cannot generate images when
an image generation provider is configured.

If the user asks for an image, the application handles
the image generation separately.

If an image is provided, analyze it accurately.

Be helpful, concise and natural.
"""


# ============================================================
# HELPERS
# ============================================================

def clean_message(message):
    if message is None:
        return ""

    return str(message).strip()


def is_image_request(message):
    if not message:
        return False

    text = message.lower().strip()

    keywords = [
        "create image",
        "generate image",
        "make image",
        "draw",
        "generate a picture",
        "create a picture",
        "image",
        "picture",
        "photo",
        "صورة",
        "صور",
        "انشئ صورة",
        "أنشئ صورة",
        "إنشاء صورة",
        "اصنع صورة",
        "أصنع صورة",
        "ارسم",
        "رسم",
        "توليد صورة",
        "توليد الصور",
        "صمم صورة",
        "صمّم صورة"
    ]

    return any(word in text for word in keywords)


def is_image_edit_request(message, image_bytes=None):
    if not image_bytes:
        return False

    if not message:
        return True

    text = message.lower()

    keywords = [
        "edit",
        "modify",
        "change",
        "remove",
        "replace",
        "transform",
        "enhance",
        "تعديل",
        "عدل",
        "عدّل",
        "غيّر",
        "غير",
        "احذف",
        "أضف",
        "اضف",
        "استبدل",
        "تحسين"
    ]

    return any(word in text for word in keywords)


# ============================================================
# XAI TEXT
# ============================================================

def xai_text_response(message, conversation=None):
    if not xai_client:
        return None

    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        if conversation:
            messages.extend(conversation)

        messages.append({
            "role": "user",
            "content": message
        })

        response = xai_client.chat.completions.create(
            model=XAI_TEXT_MODEL,
            messages=messages,
            temperature=0.7
        )

        if not response.choices:
            return None

        content = response.choices[0].message.content

        if not content:
            return None

        return content.strip()

    except Exception as e:
        print("XAI TEXT ERROR:", repr(e))
        return None


# ============================================================
# MISTRAL TEXT
# ============================================================

def mistral_text_response(message, conversation=None):
    if not mistral_client:
        return None

    for attempt in range(MISTRAL_MAX_RETRIES + 1):

        try:
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            if conversation:
                messages.extend(conversation)

            messages.append({
                "role": "user",
                "content": message
            })

            response = mistral_client.chat.complete(
                model=MISTRAL_VISION_MODEL,
                messages=messages,
                temperature=0.7
            )

            content = response.choices[0].message.content

            if content:
                return content.strip()

        except Exception as e:

            print(
                f"MISTRAL TEXT ERROR "
                f"{attempt + 1}/{MISTRAL_MAX_RETRIES + 1}:",
                repr(e)
            )

            if attempt < MISTRAL_MAX_RETRIES:
                delay = min(
                    MISTRAL_RETRY_BASE_SECONDS * (2 ** attempt),
                    30
                )

                time.sleep(delay)

    return None


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text_response(message, conversation=None):
    if not groq_client:
        return None

    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        if conversation:
            messages.extend(conversation)

        messages.append({
            "role": "user",
            "content": message
        })

        response = groq_client.chat.completions.create(
            model=GROQ_TEXT_MODEL,
            messages=messages,
            temperature=0.7
        )

        if not response.choices:
            return None

        content = response.choices[0].message.content

        if content:
            return content.strip()

    except Exception as e:
        print("GROQ TEXT ERROR:", repr(e))

    return None


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_text_response(message, conversation=None):
    if not openrouter_client:
        return None

    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        if conversation:
            messages.extend(conversation)

        messages.append({
            "role": "user",
            "content": message
        })

        response = openrouter_client.chat.completions.create(
            model=OPENROUTER_TEXT_MODEL,
            messages=messages,
            temperature=0.7
        )

        if not response.choices:
            return None

        content = response.choices[0].message.content

        if content:
            return content.strip()

    except Exception as e:
        print("OPENROUTER TEXT ERROR:", repr(e))

    return None


# ============================================================
# GEMINI TEXT
# ============================================================

def gemini_text_response(message):
    if not gemini_client:
        return None

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=message
        )

        if response and response.text:
            return response.text.strip()

    except Exception as e:
        print("GEMINI TEXT ERROR:", repr(e))

    return None


# ============================================================
# FINAL TEXT ROUTER
# ============================================================

def get_response(
    message,
    conversation_id=None,
    conversation=None
):
    message = clean_message(message)

    if not message:
        return "مرحباً! كيف يمكنني مساعدتك؟"

    print("=" * 70)
    print("TEXT REQUEST")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # --------------------------------------------------------
    # XAI
    # --------------------------------------------------------

    result = xai_text_response(
        message,
        conversation
    )

    if result:
        print("TEXT PROVIDER: XAI")
        return result

    # --------------------------------------------------------
    # MISTRAL
    # --------------------------------------------------------

    result = mistral_text_response(
        message,
        conversation
    )

    if result:
        print("TEXT PROVIDER: MISTRAL")
        return result

    # --------------------------------------------------------
    # GROQ
    # --------------------------------------------------------

    result = groq_text_response(
        message,
        conversation
    )

    if result:
        print("TEXT PROVIDER: GROQ")
        return result

    # --------------------------------------------------------
    # OPENROUTER
    # --------------------------------------------------------

    result = openrouter_text_response(
        message,
        conversation
    )

    if result:
        print("TEXT PROVIDER: OPENROUTER")
        return result

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    result = gemini_text_response(message)

    if result:
        print("TEXT PROVIDER: GEMINI")
        return result

    return (
        "تعذر الحصول على إجابة حاليًا. "
        "تحقق من مفاتيح API واتصال مزودي الذكاء الاصطناعي."
    )


# ============================================================
# IMAGE -> DATA URL
# ============================================================

def image_to_data_url(image_bytes, mime_type):
    if not image_bytes:
        return None

    if not mime_type:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


# ============================================================
# XAI VISION
# ============================================================

def xai_vision_response(
    message,
    image_bytes,
    mime_type="image/jpeg"
):
    if not xai_client or not image_bytes:
        return None

    try:
        data_url = image_to_data_url(
            image_bytes,
            mime_type
        )

        response = xai_client.chat.completions.create(
            model=XAI_VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message or "حلل هذه الصورة."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            temperature=0.3
        )

        if not response.choices:
            return None

        content = response.choices[0].message.content

        if content:
            return content.strip()

    except Exception as e:
        print("XAI VISION ERROR:", repr(e))

    return None


# ============================================================
# MISTRAL VISION
# ============================================================

def mistral_vision_response(
    message,
    image_bytes,
    mime_type="image/jpeg"
):
    if not mistral_client or not image_bytes:
        return None

    for attempt in range(MISTRAL_MAX_RETRIES + 1):

        try:
            data_url = image_to_data_url(
                image_bytes,
                mime_type
            )

            response = mistral_client.chat.complete(
                model=MISTRAL_VISION_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    message
                                    or
                                    "حلل هذه الصورة."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": data_url
                            }
                        ]
                    }
                ]
            )

            content = response.choices[0].message.content

            if content:
                return content.strip()

        except Exception as e:

            print(
                f"MISTRAL VISION ERROR "
                f"{attempt + 1}/{MISTRAL_MAX_RETRIES + 1}:",
                repr(e)
            )

            if attempt < MISTRAL_MAX_RETRIES:
                delay = min(
                    MISTRAL_RETRY_BASE_SECONDS * (2 ** attempt),
                    30
                )

                time.sleep(delay)

    return None


# ============================================================
# IMAGE UNDERSTANDING ROUTER
# ============================================================

def analyze_image(
    message,
    image_bytes,
    mime_type="image/jpeg"
):
    print("=" * 70)
    print("IMAGE UNDERSTANDING")
    print("=" * 70)

    # XAI PRIMARY
    result = xai_vision_response(
        message,
        image_bytes,
        mime_type
    )

    if result:
        print("VISION PROVIDER: XAI")
        return result

    # MISTRAL FALLBACK
    result = mistral_vision_response(
        message,
        image_bytes,
        mime_type
    )

    if result:
        print("VISION PROVIDER: MISTRAL")
        return result

    return (
        "تعذر تحليل الصورة حاليًا. "
        "تمت تجربة XAI وMistral."
    )


# ============================================================
# XAI IMAGE GENERATION
# ============================================================

def xai_generate_image(prompt):
    if not XAI_API_KEY:
        print("XAI IMAGE: API KEY NOT CONFIGURED")
        return None

    try:
        print("=" * 70)
        print("XAI IMAGE GENERATION REQUEST")
        print("=" * 70)
        print("MODEL:", XAI_IMAGE_MODEL)
        print("PROMPT:", prompt)

        response = requests.post(
            "https://api.x.ai/v1/images/generations",
            headers={
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": XAI_IMAGE_MODEL,
                "prompt": prompt
            },
            timeout=AI_REQUEST_TIMEOUT
        )

        print(
            "XAI IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:
            print(
                "XAI IMAGE ERROR:",
                response.text[:2000]
            )
            return None

        data = response.json()

        if not isinstance(data, dict):
            return None

        items = data.get("data")

        if not items:
            print("XAI IMAGE: NO DATA")
            return None

        item = items[0]

        if not isinstance(item, dict):
            return None

        url = item.get("url")

        if url:
            return {
                "url": url,
                "provider": "xAI",
                "model": XAI_IMAGE_MODEL
            }

        b64 = (
            item.get("b64_json")
            or item.get("base64")
        )

        if b64:
            return {
                "b64_json": b64,
                "provider": "xAI",
                "model": XAI_IMAGE_MODEL
            }

        print("XAI IMAGE: UNKNOWN RESPONSE FORMAT")

    except Exception as e:
        print("XAI IMAGE EXCEPTION:", repr(e))

    return None


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_generate_image(prompt):
    if not mistral_client:
        return None

    for attempt in range(MISTRAL_MAX_RETRIES + 1):

        try:
            print("=" * 70)
            print("MISTRAL IMAGE GENERATION REQUEST")
            print("=" * 70)
            print(
                "MODEL:",
                MISTRAL_IMAGE_MODEL
            )
            print("ATTEMPT:", attempt + 1)

            # Mistral image generation APIs can differ by SDK
            # version. Try the SDK method first.

            response = None

            if hasattr(
                mistral_client,
                "images"
            ):

                images_api = mistral_client.images

                if hasattr(
                    images_api,
                    "generate"
                ):

                    response = images_api.generate(
                        model=MISTRAL_IMAGE_MODEL,
                        prompt=prompt
                    )

            if response is None:
                print(
                    "MISTRAL IMAGE: "
                    "IMAGE GENERATION METHOD UNAVAILABLE"
                )

            else:

                data = getattr(
                    response,
                    "data",
                    None
                )

                if data:

                    item = data[0]

                    url = getattr(
                        item,
                        "url",
                        None
                    )

                    if url:
                        return {
                            "url": url,
                            "provider": "Mistral",
                            "model": MISTRAL_IMAGE_MODEL
                        }

                    b64 = getattr(
                        item,
                        "b64_json",
                        None
                    )

                    if b64:
                        return {
                            "b64_json": b64,
                            "provider": "Mistral",
                            "model": MISTRAL_IMAGE_MODEL
                        }

        except Exception as e:

            print(
                f"MISTRAL IMAGE ERROR "
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}:",
                repr(e)
            )

            if attempt < MISTRAL_MAX_RETRIES:

                delay = min(
                    MISTRAL_RETRY_BASE_SECONDS
                    * (2 ** attempt),
                    30
                )

                time.sleep(delay)

    return None


# ============================================================
# GROQ IMAGE FALLBACK
# ============================================================

def groq_generate_image(prompt):
    """
    Groq is kept as an optional image fallback.

    IMPORTANT:
    Groq does not necessarily expose an image-generation
    endpoint for every configured model/account.

    Therefore this function safely returns None if image
    generation is not available instead of breaking IDO AI.
    """

    if not GROQ_API_KEY:
        return None

    print("=" * 70)
    print("GROQ IMAGE FALLBACK")
    print("=" * 70)

    print(
        "GROQ IMAGE: "
        "NO IMAGE GENERATION ENDPOINT CONFIGURED"
    )

    return None


# ============================================================
# XAI IMAGE EDIT
# ============================================================

def xai_edit_image(
    prompt,
    image_bytes,
    mime_type="image/jpeg"
):
    if not XAI_API_KEY or not image_bytes:
        return None

    try:
        print("=" * 70)
        print("XAI IMAGE EDIT REQUEST")
        print("=" * 70)

        filename = "input_image"

        extension = mimetypes.guess_extension(
            mime_type
        )

        if extension:
            filename += extension

        files = {
            "image": (
                filename,
                image_bytes,
                mime_type
            )
        }

        data = {
            "model": XAI_IMAGE_MODEL,
            "prompt": prompt
        }

        response = requests.post(
            "https://api.x.ai/v1/images/edits",
            headers={
                "Authorization": f"Bearer {XAI_API_KEY}"
            },
            files=files,
            data=data,
            timeout=AI_REQUEST_TIMEOUT
        )

        print(
            "XAI IMAGE EDIT STATUS:",
            response.status_code
        )

        if response.status_code != 200:
            print(
                "XAI IMAGE EDIT ERROR:",
                response.text[:2000]
            )
            return None

        result = response.json()

        items = result.get("data")

        if not items:
            return None

        item = items[0]

        url = item.get("url")

        if url:
            return {
                "url": url,
                "provider": "xAI",
                "model": XAI_IMAGE_MODEL
            }

        b64 = (
            item.get("b64_json")
            or item.get("base64")
        )

        if b64:
            return {
                "b64_json": b64,
                "provider": "xAI",
                "model": XAI_IMAGE_MODEL
            }

    except Exception as e:
        print("XAI IMAGE EDIT EXCEPTION:", repr(e))

    return None


# ============================================================
# MISTRAL IMAGE EDIT FALLBACK
# ============================================================

def mistral_edit_image(
    prompt,
    image_bytes,
    mime_type="image/jpeg"
):
    """
    Safe Mistral fallback.

    If the installed Mistral SDK does not expose an image
    editing API, return None without crashing the application.
    """

    if not mistral_client or not image_bytes:
        return None

    print("=" * 70)
    print("MISTRAL IMAGE EDIT FALLBACK")
    print("=" * 70)

    try:

        if hasattr(
            mistral_client,
            "images"
        ):

            images_api = mistral_client.images

            if hasattr(
                images_api,
                "edit"
            ):

                response = images_api.edit(
                    model=MISTRAL_IMAGE_MODEL,
                    prompt=prompt,
                    image=image_bytes
                )

                data = getattr(
                    response,
                    "data",
                    None
                )

                if data:

                    item = data[0]

                    url = getattr(
                        item,
                        "url",
                        None
                    )

                    if url:
                        return {
                            "url": url,
                            "provider": "Mistral",
                            "model": MISTRAL_IMAGE_MODEL
                        }

                    b64 = getattr(
                        item,
                        "b64_json",
                        None
                    )

                    if b64:
                        return {
                            "b64_json": b64,
                            "provider": "Mistral",
                            "model": MISTRAL_IMAGE_MODEL
                        }

        print(
            "MISTRAL IMAGE EDIT: "
            "METHOD UNAVAILABLE"
        )

    except Exception as e:
        print(
            "MISTRAL IMAGE EDIT ERROR:",
            repr(e)
        )

    return None


# ============================================================
# FINAL IMAGE GENERATION ROUTER
# ============================================================

def generate_image(
    prompt,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):
    prompt = clean_message(prompt)

    if not prompt:
        prompt = "Create a high quality image."

    print("=" * 70)
    print("IMAGE GENERATION START")
    print("=" * 70)
    print("PROMPT:", prompt)
    print("HAS INPUT IMAGE:", bool(image_bytes))
    print("MIME TYPE:", mime_type)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # ========================================================
    # IMAGE EDITING
    # ========================================================

    if image_bytes:

        print("IMAGE EDIT MODE")

        # ----------------------------------------------------
        # XAI
        # ----------------------------------------------------

        result = xai_edit_image(
            prompt,
            image_bytes,
            mime_type or "image/jpeg"
        )

        if result:
            print("IMAGE EDIT PROVIDER: XAI")
            return result

        # ----------------------------------------------------
        # MISTRAL
        # ----------------------------------------------------

        result = mistral_edit_image(
            prompt,
            image_bytes,
            mime_type or "image/jpeg"
        )

        if result:
            print("IMAGE EDIT PROVIDER: MISTRAL")
            return result

    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    print("IMAGE GENERATION MODE")

    # --------------------------------------------------------
    # 1. XAI PRIMARY
    # --------------------------------------------------------

    result = xai_generate_image(prompt)

    if result:
        print("IMAGE PROVIDER: XAI")
        return result

    # --------------------------------------------------------
    # 2. GROQ FALLBACK
    # --------------------------------------------------------

    result = groq_generate_image(prompt)

    if result:
        print("IMAGE PROVIDER: GROQ")
        return result

    # --------------------------------------------------------
    # 3. MISTRAL FALLBACK
    # --------------------------------------------------------

    result = mistral_generate_image(prompt)

    if result:
        print("IMAGE PROVIDER: MISTRAL")
        return result

    return None


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):
    """
    Compatibility function used by app.py.
    """

    print("=" * 70)
    print("IMAGE REQUEST")
    print("MESSAGE:", message)
    print("HAS INPUT IMAGE:", bool(image_bytes))
    print("MIME TYPE:", mime_type)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    result = generate_image(
        prompt=message,
        image_bytes=image_bytes,
        mime_type=mime_type,
        conversation_id=conversation_id
    )

    if result:
        return result

    return {
        "error": (
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة XAI وGroq وMistral."
        )
    }


# ============================================================
# QUICK RESPONSE COMPATIBILITY
# ============================================================

def quick_response(message):
    return get_response(message)


# ============================================================
# DYNAMIC RESPONSE
# ============================================================

def dynamic_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None,
    conversation=None
):
    message = clean_message(message)

    print("=" * 70)
    print("DYNAMIC AI RESPONSE")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
    print("HAS IMAGE:", bool(image_bytes))
    print("=" * 70)

    # ========================================================
    # IMAGE REQUEST
    # ========================================================

    if image_bytes:

        # User uploaded an image.
        # Analyze unless the request clearly asks for editing.

        if is_image_edit_request(
            message,
            image_bytes
        ):

            print("IMAGE EDIT REQUEST DETECTED")

            result = generate_image(
                message,
                image_bytes,
                mime_type,
                conversation_id
            )

            if result:
                return result

            # If editing fails, analyze the image instead.
            analysis = analyze_image(
                message,
                image_bytes,
                mime_type or "image/jpeg"
            )

            return {
                "type": "text",
                "text": analysis
            }

        # ----------------------------------------------------
        # IMAGE UNDERSTANDING
        # ----------------------------------------------------

        print("IMAGE UNDERSTANDING REQUEST")

        analysis = analyze_image(
            message,
            image_bytes,
            mime_type or "image/jpeg"
        )

        return {
            "type": "text",
            "text": analysis
        }

    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    if is_image_request(message):

        print("IMAGE REQUEST DETECTED")

        result = generate_image(
            message,
            None,
            None,
            conversation_id
        )

        if result:
            return result

        return {
            "error": (
                "تعذر إنشاء الصورة حاليًا. "
                "تمت تجربة XAI وGroq وMistral."
            )
        }

    # ========================================================
    # NORMAL TEXT
    # ========================================================

    return {
        "type": "text",
        "text": get_response(
            message,
            conversation_id,
            conversation
        )
    }


# ============================================================
# FINAL COMPATIBILITY
# ============================================================

def ask_ai(
    message,
    conversation_id=None,
    conversation=None
):
    return get_response(
        message,
        conversation_id,
        conversation
    )


# ============================================================
# STARTUP ROUTING DISPLAY
# ============================================================

print("=" * 70)
print("FINAL PROVIDER ROUTING")
print("=" * 70)

print("""
TEXT:
    XAI
      ↓
    MISTRAL
      ↓
    GROQ
      ↓
    OPENROUTER
      ↓
    GEMINI
""")

print("""
IMAGE UNDERSTANDING:
    XAI VISION
      ↓
    MISTRAL VISION
""")

print("""
IMAGE GENERATION:
    XAI IMAGE
      ↓
    GROQ IMAGE FALLBACK
      ↓
    MISTRAL IMAGE
""")

print("""
IMAGE EDITING:
    XAI IMAGE EDIT
      ↓
    MISTRAL IMAGE EDIT
""")

print("=" * 70)
print("XAI:", "ENABLED" if XAI_API_KEY else "DISABLED")
print("MISTRAL:", "ENABLED" if MISTRAL_API_KEY else "DISABLED")
print("GROQ:", "ENABLED" if GROQ_API_KEY else "DISABLED")
print(
    "OPENROUTER:",
    "ENABLED" if OPENROUTER_API_KEY else "DISABLED"
)
print("GEMINI:", "ENABLED" if GEMINI_API_KEY else "DISABLED")
print("=" * 70)

print("COMPATIBILITY: quick_response available")
print("COMPATIBILITY: get_response(message, conversation_id=None)")
print(
    "COMPATIBILITY: "
    "get_image_response(message, image_bytes, mime_type, "
    "conversation_id=None)"
)
print("=" * 70)