# ============================================================
# brain.py
# ============================================================
# Ido AI - Unified Multi-Provider AI Brain
#
# FEATURES
# ------------------------------------------------------------
# TEXT:
#   Groq -> Mistral -> OpenRouter -> Gemini -> xAI -> Pollinations
#
# VISION:
#   Mistral -> Groq -> OpenRouter -> xAI
#
# IMAGE GENERATION:
#   xAI -> OpenRouter -> Pollinations
#
# IMAGE EDITING:
#   xAI -> OpenRouter
#
# IMPORTANT:
#   Vision is ONLY for understanding/analyzing images.
#   Image editing uses real image-editing endpoints.
#
# Compatible with:
#   app.py
#   api.py
#
# get_response(message, conversation_id=None)
# get_image_response(message, image_bytes, mime_type,
#                     conversation_id=None)
# ============================================================

import os
import base64
import time
import requests
from urllib.parse import quote

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# TIMEOUTS
# ============================================================

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


# ============================================================
# PROVIDER COOLDOWN
# ============================================================

CIRCUIT_BREAK_SECONDS = int(
    os.getenv(
        "PROVIDER_COOLDOWN_SECONDS",
        "60"
    )
)

_provider_disabled_until = {}


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
        f"{name}: TEMPORARILY DISABLED "
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
        404,
        429
    ):
        disable_provider(
            name,
            f"HTTP {status_code}"
        )


# ============================================================
# HELPERS
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
            f"{provider}: RESPONSE:",
            response.text[:1500]
        )

        return None


def image_to_data_url(
    image_bytes,
    mime_type
):

    if not image_bytes:
        return None

    if not mime_type:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )

    return (
        f"data:{mime_type};base64,"
        f"{encoded}"
    )


def extract_text_from_response(
    data
):

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

    if not isinstance(
        message,
        dict
    ):
        return None

    content = message.get(
        "content"
    )

    if isinstance(
        content,
        str
    ):
        return clean_answer(
            content
        )

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

        if parts:

            return clean_answer(
                "\n".join(parts)
            )

    return None


def extract_image_from_response(
    data
):

    if not isinstance(
        data,
        dict
    ):
        return None

    # --------------------------------------------------------
    # Standard image API response
    # --------------------------------------------------------

    items = data.get(
        "data"
    )

    if isinstance(
        items,
        list
    ):

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            url = item.get(
                "url"
            )

            if url:
                return url

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

    # --------------------------------------------------------
    # Responses containing output
    # --------------------------------------------------------

    output = data.get(
        "output"
    )

    if isinstance(
        output,
        list
    ):

        for block in output:

            if not isinstance(
                block,
                dict
            ):
                continue

            content = block.get(
                "content",
                []
            )

            if not isinstance(
                content,
                list
            ):
                continue

            for item in content:

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                url = item.get(
                    "url"
                )

                if url:
                    return url

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

    return None


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash"
)

ENABLE_GEMINI = (
    os.getenv(
        "ENABLE_GEMINI",
        "false"
    ).lower()
    == "true"
)


# Gemini SDK is optional.
try:

    from google import genai
    from google.genai.types import HttpOptions

except Exception:

    genai = None
    HttpOptions = None


gemini_client = None


if (
    ENABLE_GEMINI
    and GEMINI_API_KEY
    and genai
):

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print(
            "GEMINI CLIENT: READY"
        )

        print(
            "GEMINI MODEL:",
            GEMINI_MODEL
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
        "(disabled or API key unavailable)"
    )


def ask_gemini(
    message
):

    if not ENABLE_GEMINI:
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
            "Trying Gemini..."
        )

        response = (
            gemini_client
            .models
            .generate_content(
                model=GEMINI_MODEL,
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
                "Gemini response received."
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Gemini ERROR:",
            exc
        )

        text = str(
            exc
        )

        if (
            "429" in text
            or
            "RESOURCE_EXHAUSTED"
            in text
        ):

            disable_provider(
                "GEMINI",
                "quota"
            )

        return None


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_URL = (
    "https://api.groq.com/openai/v1/"
    "chat/completions"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

# IMPORTANT:
# Keep this configurable because availability can differ
# between Groq accounts.
GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


if GROQ_API_KEY:

    print(
        "GROQ CLIENT: READY"
    )

    print(
        "GROQ MODEL:",
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
                            (
                                "You are Ido AI. "
                                "Answer clearly and helpfully. "
                                "If the user speaks Arabic, "
                                "answer in Arabic."
                            )
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

        answer = extract_text_from_response(
            data
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Groq ERROR:",
            exc
        )

        return None


# ============================================================
# MISTRAL
# ============================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_URL = (
    "https://api.mistral.ai/v1/"
    "chat/completions"
)

# Current 2026 multimodal Mistral model.
MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-medium-3-5"
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-medium-3-5"
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
                            "system",

                        "content":
                            (
                                "You are Ido AI. "
                                "Be accurate, helpful, "
                                "and natural."
                            )
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

        answer = extract_text_from_response(
            data
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
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/"
    "chat/completions"
)

OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)

OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-5.4"
)

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "openai/gpt-5.4"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-5.4-image-2"
)


if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
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

        "HTTP-Referer":
            "https://ido-ai-production.up.railway.app",

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

            headers=openrouter_headers(),

            json={

                "model":
                    OPENROUTER_TEXT_MODEL,

                "messages": [

                    {
                        "role":
                            "system",

                        "content":
                            (
                                "You are Ido AI. "
                                "Answer naturally and "
                                "helpfully."
                            )
                    },

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

        answer = extract_text_from_response(
            data
        )

        if answer:

            print(
                "OpenRouter response received."
            )

            return answer

        return None

    except Exception as exc:

        print(
            "OpenRouter ERROR:",
            exc
        )

        return None


# ============================================================
# XAI / GROK
# ============================================================

XAI_API_KEY = os.getenv(
    "XAI_API_KEY"
)

XAI_CHAT_URL = (
    "https://api.x.ai/v1/"
    "chat/completions"
)

XAI_MODEL = os.getenv(
    "XAI_MODEL",
    "grok-4.5"
)

XAI_IMAGE_URL = (
    "https://api.x.ai/v1/"
    "images/generations"
)

XAI_IMAGE_EDIT_URL = (
    "https://api.x.ai/v1/"
    "images/edits"
)

XAI_IMAGE_MODEL = os.getenv(
    "XAI_IMAGE_MODEL",
    "grok-imagine-image-quality"
)


if XAI_API_KEY:

    print(
        "XAI CLIENT: READY"
    )

    print(
        "XAI MODEL:",
        XAI_MODEL
    )

    print(
        "XAI IMAGE MODEL:",
        XAI_IMAGE_MODEL
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

        print(
            "Trying xAI..."
        )

        response = requests.post(

            XAI_CHAT_URL,

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

        answer = extract_text_from_response(
            data
        )

        if answer:

            print(
                "xAI response received."
            )

            return answer

        return None

    except Exception as exc:

        print(
            "xAI ERROR:",
            exc
        )

        return None


# ============================================================
# POLLINATIONS
# ============================================================

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

POLLINATIONS_CHAT_URL = (
    "https://gen.pollinations.ai/v1/"
    "chat/completions"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/image/"
)

POLLINATIONS_TEXT_MODEL = os.getenv(
    "POLLINATIONS_TEXT_MODEL",
    "openai"
)

POLLINATIONS_IMAGE_MODEL = os.getenv(
    "POLLINATIONS_IMAGE_MODEL",
    "flux"
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

        answer = extract_text_from_response(
            data
        )

        if answer:

            print(
                "Pollinations response received."
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Pollinations ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image_xai(
    prompt
):

    if not XAI_API_KEY:
        return None

    if not provider_available(
        "XAI_IMAGE"
    ):
        return None

    try:

        print(
            "Trying xAI IMAGE GENERATION..."
        )

        response = requests.post(

            XAI_IMAGE_URL,

            headers={
                "Authorization":
                    f"Bearer {XAI_API_KEY}",

                "Content-Type":
                    "application/json"
            },

            json={

                "model":
                    XAI_IMAGE_MODEL,

                "prompt":
                    prompt,

                "n":
                    1
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI IMAGE RESPONSE:",
                response.text[:1500]
            )

            provider_failure(
                "XAI_IMAGE",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI IMAGE"
        )

        if not data:
            return None

        image = extract_image_from_response(
            data
        )

        if image:

            print(
                "xAI IMAGE GENERATION: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "xAI IMAGE ERROR:",
            exc
        )

        return None


def generate_image_openrouter(
    prompt
):

    if not OPENROUTER_API_KEY:
        return None

    if not provider_available(
        "OPENROUTER_IMAGE"
    ):
        return None

    try:

        print(
            "Trying OpenRouter IMAGE GENERATION..."
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

        image = extract_image_from_response(
            data
        )

        if image:

            print(
                "OpenRouter IMAGE: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "OpenRouter IMAGE ERROR:",
            exc
        )

        return None


def generate_image_pollinations(
    prompt
):

    if not POLLINATIONS_API_KEY:
        return None

    if not provider_available(
        "POLLINATIONS_IMAGE"
    ):
        return None

    try:

        print(
            "Trying Pollinations IMAGE..."
        )

        url = (
            POLLINATIONS_IMAGE_URL
            +
            quote(
                prompt,
                safe=""
            )
        )

        response = requests.get(

            url,

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
                    1024
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
                response.text[:1000]
            )

            provider_failure(
                "POLLINATIONS_IMAGE",
                response.status_code
            )

            return None

        content_type = (
            response.headers.get(
                "Content-Type",
                "image/jpeg"
            )
        )

        if not content_type.startswith(
            "image/"
        ):
            return None

        encoded = base64.b64encode(
            response.content
        ).decode(
            "utf-8"
        )

        print(
            "Pollinations IMAGE: SUCCESS"
        )

        return (
            f"data:{content_type};base64,"
            f"{encoded}"
        )

    except Exception as exc:

        print(
            "Pollinations IMAGE ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE GENERATION ROUTER
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
                "اكتب وصف الصورة "
                "التي تريد إنشاءها.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)

    print(
        "IMAGE GENERATION STARTED"
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 60)


    # --------------------------------------------------------
    # 1. xAI
    # --------------------------------------------------------

    image = generate_image_xai(
        prompt
    )

    if image:

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                image,

            "provider":
                "xAI"
        }


    # --------------------------------------------------------
    # 2. OpenRouter
    # --------------------------------------------------------

    image = generate_image_openrouter(
        prompt
    )

    if image:

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                image,

            "provider":
                "OpenRouter"
        }


    # --------------------------------------------------------
    # 3. Pollinations
    # --------------------------------------------------------

    image = generate_image_pollinations(
        prompt
    )

    if image:

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                image,

            "provider":
                "Pollinations"
        }


    return {

        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة مولدات الصور المتاحة "
            "ولكن لم يُرجع أي مولد صورة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# IMAGE EDITING - xAI
# ============================================================

def edit_image_xai(
    prompt,
    image_bytes,
    mime_type
):

    if not XAI_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "XAI_IMAGE_EDIT"
    ):
        return None

    try:

        print(
            "Trying xAI IMAGE EDIT..."
        )

        image_data_url = image_to_data_url(
            image_bytes,
            mime_type
        )

        if not image_data_url:
            return None

        response = requests.post(

            XAI_IMAGE_EDIT_URL,

            headers={
                "Authorization":
                    f"Bearer {XAI_API_KEY}",

                "Content-Type":
                    "application/json"
            },

            json={

                "model":
                    XAI_IMAGE_MODEL,

                "prompt":
                    prompt,

                "image":
                    {
                        "url":
                            image_data_url
                    }
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI IMAGE EDIT STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI IMAGE EDIT RESPONSE:",
                response.text[:2000]
            )

            provider_failure(
                "XAI_IMAGE_EDIT",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI IMAGE EDIT"
        )

        if not data:
            return None

        image = extract_image_from_response(
            data
        )

        if image:

            print(
                "xAI IMAGE EDIT: SUCCESS"
            )

            return image

        print(
            "xAI IMAGE EDIT returned no image."
        )

        return None

    except Exception as exc:

        print(
            "xAI IMAGE EDIT ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE EDITING - OPENROUTER
# ============================================================

def edit_image_openrouter(
    prompt,
    image_bytes,
    mime_type
):

    if not OPENROUTER_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "OPENROUTER_IMAGE_EDIT"
    ):
        return None

    try:

        print(
            "Trying OpenRouter IMAGE EDIT..."
        )

        image_data_url = image_to_data_url(
            image_bytes,
            mime_type
        )

        if not image_data_url:
            return None

        # OpenRouter's image endpoint accepts
        # reference images for image-to-image work.

        response = requests.post(

            OPENROUTER_IMAGE_URL,

            headers=openrouter_headers(),

            json={

                "model":
                    OPENROUTER_IMAGE_MODEL,

                "prompt":
                    prompt,

                "images": [

                    image_data_url

                ],

                "n":
                    1
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter IMAGE EDIT STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter IMAGE EDIT RESPONSE:",
                response.text[:2000]
            )

            provider_failure(
                "OPENROUTER_IMAGE_EDIT",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter IMAGE EDIT"
        )

        if not data:
            return None

        image = extract_image_from_response(
            data
        )

        if image:

            print(
                "OpenRouter IMAGE EDIT: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "OpenRouter IMAGE EDIT ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE EDITING ROUTER
# ============================================================

def edit_image(
    prompt,
    image_bytes,
    mime_type
):

    prompt = clean_answer(
        prompt
    )

    if not image_bytes:

        return {

            "answer":
                "لم يتم إرسال صورة صالحة.",

            "imageUrl":
                "",

            "provider":
                None
        }


    if not prompt:

        prompt = (
            "حافظ على الصورة كما هي "
            "وعدّلها حسب الطلب."
        )


    print("=" * 60)

    print(
        "IMAGE EDITING STARTED"
    )

    print(
        "EDIT PROMPT:",
        prompt
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # 1. xAI
    # --------------------------------------------------------

    image = edit_image_xai(

        prompt,
        image_bytes,
        mime_type
    )

    if image:

        return {

            "answer":
                "تم تعديل الصورة بنجاح.",

            "imageUrl":
                image,

            "provider":
                "xAI"
        }


    print(
        "xAI IMAGE EDIT failed."
    )


    # --------------------------------------------------------
    # 2. OpenRouter
    # --------------------------------------------------------

    image = edit_image_openrouter(

        prompt,
        image_bytes,
        mime_type
    )

    if image:

        return {

            "answer":
                "تم تعديل الصورة بنجاح.",

            "imageUrl":
                image,

            "provider":
                "OpenRouter"
        }


    print(
        "OpenRouter IMAGE EDIT failed."
    )


    return {

        "answer":
            "تعذر تعديل الصورة حاليًا. "
            "تمت تجربة خدمات تعديل الصور "
            "المتاحة ولم تُرجع صورة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# IMAGE UNDERSTANDING
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

        print(
            "Trying Mistral Vision..."
        )

        image_url = image_to_data_url(
            image_bytes,
            mime_type
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

        answer = extract_text_from_response(
            data
        )

        return answer

    except Exception as exc:

        print(
            "Mistral Vision ERROR:",
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

        print(
            "Trying Groq Vision..."
        )

        image_url = image_to_data_url(
            image_bytes,
            mime_type
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

        return extract_text_from_response(
            data
        )

    except Exception as exc:

        print(
            "Groq Vision ERROR:",
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

        print(
            "Trying OpenRouter Vision..."
        )

        image_url = image_to_data_url(
            image_bytes,
            mime_type
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

        return extract_text_from_response(
            data
        )

    except Exception as exc:

        print(
            "OpenRouter Vision ERROR:",
            exc
        )

        return None


# ============================================================
# xAI VISION
# ============================================================

def ask_xai_image(
    message,
    image_bytes,
    mime_type
):

    if not XAI_API_KEY:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "XAI_VISION"
    ):
        return None

    try:

        print(
            "Trying xAI Vision..."
        )

        image_url = image_to_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(

            XAI_CHAT_URL,

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
            "xAI Vision Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI Vision Response:",
                response.text[:1500]
            )

            provider_failure(
                "XAI_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI Vision"
        )

        if not data:
            return None

        return extract_text_from_response(
            data
        )

    except Exception as exc:

        print(
            "xAI Vision ERROR:",
            exc
        )

        return None


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_GENERATION_WORDS = [

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

    "generate an image",
    "generate image",

    "create an image",
    "create image",

    "make an image",
    "make image",

    "draw an image",
    "draw image",

    "create a picture",
    "generate a picture"
]


IMAGE_EDIT_WORDS = [

    "عدل الصورة",
    "عدّل الصورة",
    "تعديل الصورة",

    "عدل على الصورة",
    "عدّل على الصورة",

    "غير الصورة",
    "غيّر الصورة",

    "غير لون",
    "غيّر لون",

    "غيّر السيارة",
    "غير السيارة",

    "change the image",
    "edit the image",

    "edit image",
    "modify image",

    "change the color",
    "change color",

    "remove from the image",
    "add to the image",

    "replace in the image"
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
        for word in IMAGE_GENERATION_WORDS
    )


def is_image_edit_request(
    message
):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    return any(
        word.lower() in text
        for word in IMAGE_EDIT_WORDS
    )


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
        "create a picture of"
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
# QUICK RESPONSES
# ============================================================

QUICK_RESPONSES = {

    "hello":
        (
            "السلام عليكم ورحمة الله وبركاته. "
            "أنا Ido AI، كيف يمكنني مساعدتك؟"
        ),

    "hi":
        (
            "السلام عليكم ورحمة الله وبركاته. "
            "أنا Ido AI، كيف يمكنني مساعدتك؟"
        ),

    "مرحبا":
        (
            "السلام عليكم ورحمة الله وبركاته. "
            "مرحبًا بك، كيف يمكنني مساعدتك؟"
        ),

    "سلام":
        (
            "وعليكم السلام ورحمة الله وبركاته. "
            "كيف يمكنني مساعدتك؟"
        ),

    "اسمك":
        "أنا Ido AI.",

    "ما اسمك":
        "أنا Ido AI.",

    "كيف حالك":
        (
            "أنا بخير، شكرًا لسؤالك. "
            "كيف يمكنني مساعدتك؟"
        ),

    "من صنعك":
        (
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI."
        ),

    "من طورك":
        (
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI."
        ),

    "من بناك":
        (
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI."
        ),

    "من برمجك":
        (
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI."
        ),

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

    text = str(
        message
    ).lower()

    for key, value in (
        QUICK_RESPONSES.items()
    ):

        if key.lower() in text:

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


    # --------------------------------------------------------
    # IMAGE GENERATION FROM TEXT
    # --------------------------------------------------------

    if is_image_generation_request(
        original_message
    ):

        prompt = get_image_prompt(
            original_message
        )

        if not prompt:

            return {

                "answer":
                    "اكتب وصف الصورة "
                    "التي تريد إنشاءها.",

                "imageUrl":
                    "",

                "provider":
                    None
            }

        return generate_image(
            prompt
        )


    # --------------------------------------------------------
    # QUICK RESPONSE
    # --------------------------------------------------------

    quick = quick_response(
        original_message
    )

    if quick:

        return quick


    # --------------------------------------------------------
    # TEXT PROVIDER ROUTER
    # --------------------------------------------------------

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
                f"TEXT ROUTE SUCCESS: "
                f"{name}"
            )

            return answer


        print(
            f"{name} failed. "
            "Trying next provider..."
        )


    return (
        "أنا Ido AI، لكن جميع مزودي "
        "الذكاء الاصطناعي المتاحين "
        "فشلوا حاليًا. "
        "تحقق من المفاتيح والرصيد."
    )


# ============================================================
# MAIN IMAGE ROUTER
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

    print(
        "IMAGE REQUEST RECEIVED"
    )

    print(
        "IMAGE MIME TYPE:",
        mime_type
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print(
        "IMAGE QUESTION:",
        message
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 60)


    # ========================================================
    # EDIT REQUEST
    # ========================================================

    if is_image_edit_request(
        message
    ):

        print(
            "REQUEST TYPE: IMAGE EDIT"
        )

        result = edit_image(

            message,
            image_bytes,
            mime_type
        )

        return result


    # ========================================================
    # VISION / IMAGE UNDERSTANDING
    # ========================================================

    print(
        "REQUEST TYPE: IMAGE UNDERSTANDING"
    )


    vision_routes = [

        (
            "MISTRAL_VISION",
            ask_mistral_image
        ),

        (
            "GROQ_VISION",
            ask_groq_image
        ),

        (
            "OPENROUTER_VISION",
            ask_openrouter_image
        ),

        (
            "XAI_VISION",
            ask_xai_image
        )
    ]


    for name, function in vision_routes:


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
                f"{name} ROUTER ERROR:",
                exc
            )

            answer = None


        if answer:

            print(
                f"VISION ROUTE SUCCESS: "
                f"{name}"
            )

            return answer


        print(
            f"{name} failed. "
            "Trying next vision provider..."
        )


    return (
        "تعذر تحليل الصورة حاليًا. "
        "تمت تجربة جميع مزودي الرؤية "
        "المتاحين."
    )


# ============================================================
# STARTUP
# ============================================================

print("=" * 60)

print(
    "BRAIN.PY LOADED"
)

print(
    "TEXT ROUTE:"
)

print(
    "GROQ -> MISTRAL -> OPENROUTER -> "
    "GEMINI -> XAI -> POLLINATIONS"
)

print(
    "VISION ROUTE:"
)

print(
    "MISTRAL -> GROQ -> OPENROUTER -> XAI"
)

print(
    "IMAGE GENERATION ROUTE:"
)

print(
    "XAI -> OPENROUTER -> POLLINATIONS"
)

print(
    "IMAGE EDITING ROUTE:"
)

print(
    "XAI -> OPENROUTER"
)

print("=" * 60)