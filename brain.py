# brain.py
# ============================================================
# Ido AI - Unified Multi-Provider AI Brain
#
# PROVIDER ORDER:
#   1. Groq
#   2. Mistral
#   3. OpenRouter
#   4. Gemini
#   5. xAI / Grok
#   6. Pollinations
#
# CAPABILITIES:
#   TEXT       -> all available text providers
#   VISION     -> all available vision providers
#   GENERATE   -> every configured image-generation provider
#   EDIT       -> every configured image-edit provider
#
# IMPORTANT:
#   - Providers are never treated as one single model.
#   - Every provider is attempted independently.
#   - A failure moves the request to the next provider.
#   - TEXT, VISION, GENERATE and EDIT are separate routes.
#   - conversation_id is accepted for compatibility with app.py
#     and api.py.
# ============================================================

import os
import base64
import time
import re
import requests

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
        "60"
    )
)

REQUEST_TIMEOUT = (
    CONNECT_TIMEOUT,
    READ_TIMEOUT
)


# ============================================================
# PROVIDER COOLDOWN
# ============================================================

COOLDOWN_SECONDS = int(
    os.getenv(
        "PROVIDER_COOLDOWN_SECONDS",
        "60"
    )
)

_provider_disabled_until = {}


def provider_available(name):
    """
    Return True when the provider is available.
    """

    disabled_until = _provider_disabled_until.get(
        name,
        0
    )

    return time.time() >= disabled_until


def disable_provider(
    name,
    reason="temporary failure"
):
    """
    Temporarily disable a provider.
    """

    _provider_disabled_until[name] = (
        time.time()
        + COOLDOWN_SECONDS
    )

    print(
        f"{name}: TEMPORARILY DISABLED "
        f"for {COOLDOWN_SECONDS}s - {reason}"
    )


def provider_failure(
    name,
    status_code=None,
    reason=None
):
    """
    Disable a provider for authentication,
    quota or serious HTTP errors.
    """

    if status_code in (
        401,
        403,
        429
    ):
        disable_provider(
            name,
            reason or f"HTTP {status_code}"
        )

    elif status_code in (
        408,
        500,
        502,
        503,
        504
    ):
        disable_provider(
            name,
            reason or f"HTTP {status_code}"
        )


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_answer(value):
    """
    Safely convert a provider response to text.
    """

    if value is None:
        return None

    try:
        value = str(value).strip()
    except Exception:
        return None

    return value or None


def request_json(
    response,
    provider
):
    """
    Safely decode JSON.
    """

    try:
        return response.json()

    except Exception as exc:

        print(
            f"{provider}: INVALID JSON:",
            exc
        )

        try:
            print(
                f"{provider}: BODY:",
                response.text[:1500]
            )
        except Exception:
            pass

        return None


def make_data_url(
    image_bytes,
    mime_type
):
    """
    Convert raw image bytes to a data URL.
    """

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{mime_type};base64,"
        f"{encoded}"
    )


def extract_text_content(content):
    """
    Handle normal string content and
    some providers returning content arrays.
    """

    if content is None:
        return None

    if isinstance(content, str):
        return clean_answer(content)

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, str):
                parts.append(item)
                continue

            if not isinstance(item, dict):
                continue

            text = (
                item.get("text")
                or item.get("content")
            )

            if text:
                parts.append(
                    str(text)
                )

        if parts:
            return clean_answer(
                "\n".join(parts)
            )

    if isinstance(content, dict):

        text = (
            content.get("text")
            or content.get("content")
        )

        if text:
            return clean_answer(text)

    return None


def extract_openai_text(data):
    """
    Extract text from OpenAI-compatible responses.
    """

    if not isinstance(data, dict):
        return None

    choices = data.get(
        "choices",
        []
    )

    if not choices:
        return None

    first = choices[0]

    if not isinstance(first, dict):
        return None

    message = first.get(
        "message",
        {}
    )

    if not isinstance(message, dict):
        return None

    return extract_text_content(
        message.get("content")
    )


def extract_image_from_response(
    data
):
    """
    Extract an image URL or base64 image
    from common image API response formats.
    """

    if not isinstance(data, dict):
        return None

    items = data.get(
        "data",
        []
    )

    if not isinstance(items, list):
        return None

    if not items:
        return None

    item = items[0]

    if not isinstance(item, dict):
        return None

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    image_url = item.get(
        "url"
    )

    if image_url:
        return image_url

    # --------------------------------------------------------
    # Base64
    # --------------------------------------------------------

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
    # Some APIs use image_url
    # --------------------------------------------------------

    image_url = item.get(
        "image_url"
    )

    if isinstance(
        image_url,
        dict
    ):
        image_url = image_url.get(
            "url"
        )

    if image_url:
        return image_url

    return None


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

ENABLE_GEMINI = (
    os.getenv(
        "ENABLE_GEMINI",
        "false"
    ).lower()
    == "true"
)

gemini_client = None

try:

    from google import genai

except Exception:

    genai = None


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
        "(disabled, key unavailable, "
        "or SDK unavailable)"
    )


def ask_gemini(
    message,
    conversation_id=None
):

    if not gemini_client:
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

        text = str(exc)

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
    "openai/gpt-oss-20b"
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/"
    "llama-4-scout-17b-16e-instruct"
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


def groq_headers():

    return {
        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json"
    }


def ask_groq(
    message,
    conversation_id=None
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

            headers=groq_headers(),

            json={

                "model":
                    GROQ_MODEL,

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

        answer = extract_openai_text(
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


def ask_groq_vision(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
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

        image_url = make_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(

            GROQ_URL,

            headers=groq_headers(),

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

        answer = extract_openai_text(
            data
        )

        if answer:
            return answer

        return None

    except Exception as exc:

        print(
            "Groq Vision ERROR:",
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


def mistral_headers():

    return {
        "Authorization":
            f"Bearer {MISTRAL_API_KEY}",

        "Content-Type":
            "application/json"
    }


def ask_mistral(
    message,
    conversation_id=None
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

            headers=mistral_headers(),

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

        answer = extract_openai_text(
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


def ask_mistral_vision(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
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

        image_url = make_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(

            MISTRAL_URL,

            headers=mistral_headers(),

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

        answer = extract_openai_text(
            data
        )

        if answer:
            return answer

        return None

    except Exception as exc:

        print(
            "Mistral Vision ERROR:",
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
    "openai/gpt-oss-20b"
)

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-image-1"
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

        "X-Title":
            "Ido AI"
    }


def ask_openrouter(
    message,
    conversation_id=None
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

        answer = extract_openai_text(
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


def ask_openrouter_vision(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
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

        image_url = make_data_url(
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

            provider_failure(
                "OPENROUTER_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter Vision"
        )

        answer = extract_openai_text(
            data
        )

        if answer:
            return answer

        return None

    except Exception as exc:

        print(
            "OpenRouter Vision ERROR:",
            exc
        )

        return None


def generate_image_openrouter(
    prompt,
    image_bytes=None,
    mime_type=None
):

    if not OPENROUTER_API_KEY:
        return None

    if not provider_available(
        "OPENROUTER_IMAGE"
    ):
        return None

    try:

        print(
            "Trying OpenRouter Image..."
        )

        payload = {

            "model":
                OPENROUTER_IMAGE_MODEL,

            "prompt":
                prompt,

            "n":
                1
        }

        # ----------------------------------------------------
        # Reference image support
        # ----------------------------------------------------

        if image_bytes:

            payload[
                "input_references"
            ] = [

                make_data_url(
                    image_bytes,
                    mime_type or "image/png"
                )
            ]

        response = requests.post(

            OPENROUTER_IMAGE_URL,

            headers=openrouter_headers(),

            json=payload,

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter Image Response:",
                response.text[:1500]
            )

            provider_failure(
                "OPENROUTER_IMAGE",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter Image"
        )

        return extract_image_from_response(
            data
        )

    except Exception as exc:

        print(
            "OpenRouter Image ERROR:",
            exc
        )

        return None


# ============================================================
# XAI / GROK
# ============================================================

XAI_API_KEY = os.getenv(
    "XAI_API_KEY"
)

XAI_URL = (
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

XAI_EDIT_URL = (
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


def xai_headers():

    return {

        "Authorization":
            f"Bearer {XAI_API_KEY}",

        "Content-Type":
            "application/json"
    }


def ask_xai(
    message,
    conversation_id=None
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
            "Trying xAI / Grok..."
        )

        response = requests.post(

            XAI_URL,

            headers=xai_headers(),

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

        answer = extract_openai_text(
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


def ask_xai_vision(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
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

        image_url = make_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(

            XAI_URL,

            headers=xai_headers(),

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

            provider_failure(
                "XAI_VISION",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI Vision"
        )

        answer = extract_openai_text(
            data
        )

        if answer:
            return answer

        return None

    except Exception as exc:

        print(
            "xAI Vision ERROR:",
            exc
        )

        return None


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
            "Trying xAI Image Generation..."
        )

        response = requests.post(

            XAI_IMAGE_URL,

            headers=xai_headers(),

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
            "xAI Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI Image Response:",
                response.text[:1500]
            )

            provider_failure(
                "XAI_IMAGE",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI Image"
        )

        return extract_image_from_response(
            data
        )

    except Exception as exc:

        print(
            "xAI Image ERROR:",
            exc
        )

        return None


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
        "XAI_EDIT"
    ):
        return None

    try:

        print(
            "Trying xAI Image Editing..."
        )

        image_url = make_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(

            XAI_EDIT_URL,

            headers=xai_headers(),

            json={

                "model":
                    XAI_IMAGE_MODEL,

                "prompt":
                    prompt,

                "image": {
                    "url":
                        image_url
                }
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI Edit Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI Edit Response:",
                response.text[:1500]
            )

            provider_failure(
                "XAI_EDIT",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI Edit"
        )

        return extract_image_from_response(
            data
        )

    except Exception as exc:

        print(
            "xAI EDIT ERROR:",
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
    message,
    conversation_id=None
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

            provider_failure(
                "POLLINATIONS",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "Pollinations"
        )

        answer = extract_openai_text(
            data
        )

        if answer:
            return answer

        return None

    except Exception as exc:

        print(
            "Pollinations ERROR:",
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
            "Trying Pollinations Image..."
        )

        encoded_prompt = (
            requests.utils.quote(
                prompt,
                safe=""
            )
        )

        url = (
            POLLINATIONS_IMAGE_URL
            +
            encoded_prompt
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
            "Pollinations Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            provider_failure(
                "POLLINATIONS_IMAGE",
                response.status_code
            )

            return None

        content_type = (
            response.headers.get(
                "Content-Type",
                "image/png"
            )
        )

        encoded = base64.b64encode(
            response.content
        ).decode("utf-8")

        return (
            f"data:{content_type};base64,"
            f"{encoded}"
        )

    except Exception as exc:

        print(
            "Pollinations Image ERROR:",
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

    "generate a picture",
    "create a picture"
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

    "اجعل السيارة",
    "خل السيارة",

    "احذف من الصورة",
    "أزل من الصورة",
    "ازالة من الصورة",

    "أضف إلى الصورة",
    "اضف الى الصورة",

    "بدل في الصورة",
    "بدّل في الصورة",

    "edit the image",
    "edit image",

    "modify the image",
    "modify image",

    "change the image",
    "change image",

    "change the color",
    "remove from the image",

    "add to the image",
    "replace in the image"
]


def contains_any(
    text,
    words
):

    lower = text.lower()

    return any(
        word.lower() in lower
        for word in words
    )


def is_image_generation_request(
    message
):

    if not message:
        return False

    return contains_any(
        str(message),
        IMAGE_GENERATION_WORDS
    )


def is_image_edit_request(
    message,
    has_image=False
):

    if not message:
        return False

    text = str(
        message
    ).strip()

    if contains_any(
        text,
        IMAGE_EDIT_WORDS
    ):
        return True

    # --------------------------------------------------------
    # If an image is attached and the user uses common
    # modification language, treat it as an edit.
    # --------------------------------------------------------

    if has_image:

        edit_patterns = [

            r"\bغي[ّر]+",
            r"\bاجعل\b",
            r"\bبدل\b",
            r"\bأضف\b",
            r"\bاضف\b",
            r"\bاحذف\b",
            r"\bأزل\b",

            r"\bchange\b",
            r"\bedit\b",
            r"\bmodify\b",
            r"\bremove\b",
            r"\badd\b",
            r"\breplace\b"
        ]

        for pattern in edit_patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                return True

    return False


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

        "generate an image",
        "create an image",
        "make an image"
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

    text = str(
        message
    ).strip().lower()

    # Exact first
    if text in QUICK_RESPONSES:

        return QUICK_RESPONSES[
            text
        ]

    # Then substring
    for key, value in (
        QUICK_RESPONSES.items()
    ):

        if key.lower() in text:

            return value

    return None


# ============================================================
# TEXT ROUTER
# ============================================================

TEXT_ROUTES = [

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


def get_response(
    message,
    conversation_id=None
):

    """
    Main text entry point.

    conversation_id is intentionally accepted so
    app.py and api.py can call this function safely.
    """

    if not message:
        return "اكتب رسالة أولًا."

    original_message = str(
        message
    ).strip()

    if not original_message:
        return "اكتب رسالة أولًا."

    # --------------------------------------------------------
    # IMAGE GENERATION WITHOUT ATTACHED IMAGE
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
    # QUICK RESPONSES
    # --------------------------------------------------------

    quick = quick_response(
        original_message
    )

    if quick:
        return quick

    # --------------------------------------------------------
    # NORMAL TEXT FALLBACK
    # --------------------------------------------------------

    for name, function in TEXT_ROUTES:

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(cooldown)"
            )

            continue

        try:

            answer = function(
                original_message,
                conversation_id
            )

        except TypeError:

            # Compatibility fallback for any
            # older provider function.
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
                "TEXT ROUTE SUCCESS:",
                name
            )

            return answer

        print(
            f"{name} failed. "
            "Trying next provider..."
        )

    return (
        "أنا Ido AI، لكن لم يتمكن أي "
        "مزود متاح من الإجابة حاليًا. "
        "تحقق من مفاتيح API والرصيد "
        "وحدود الاستخدام."
    )


# ============================================================
# VISION ROUTES
# ============================================================

VISION_ROUTES = [

    (
        "GROQ_VISION",
        ask_groq_vision
    ),

    (
        "MISTRAL_VISION",
        ask_mistral_vision
    ),

    (
        "OPENROUTER_VISION",
        ask_openrouter_vision
    ),

    (
        "XAI_VISION",
        ask_xai_vision
    )
]


def analyze_image(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
):

    """
    Analyze an image.

    All available vision providers are tried in order.
    """

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
            "ما الذي يظهر فيها بالتفصيل."
        )

    message = str(
        message
    ).strip()

    for name, function in VISION_ROUTES:

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(cooldown)"
            )

            continue

        try:

            answer = function(

                message,

                image_bytes,

                mime_type,

                conversation_id

            )

        except TypeError:

            answer = function(
                message,
                image_bytes,
                mime_type
            )

        except Exception as exc:

            print(
                f"{name} ERROR:",
                exc
            )

            answer = None

        if answer:

            print(
                "VISION ROUTE SUCCESS:",
                name
            )

            return answer

        print(
            f"{name} failed. "
            "Trying next vision provider..."
        )

    return (
        "تعذر تحليل الصورة حاليًا. "
        "حاول مرة أخرى أو تحقق من "
        "مفاتيح مزودي الرؤية."
    )


# ============================================================
# IMAGE GENERATION ROUTER
# ============================================================

IMAGE_GENERATION_ROUTES = [

    (
        "XAI_IMAGE",
        generate_image_xai
    ),

    (
        "POLLINATIONS_IMAGE",
        generate_image_pollinations
    ),

    (
        "OPENROUTER_IMAGE",
        generate_image_openrouter
    )
]


def generate_image(
    prompt
):

    """
    Generate a new image.

    The router tries every configured image provider.
    """

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
        "IMAGE PROMPT:",
        prompt
    )

    print("=" * 60)

    for name, function in (
        IMAGE_GENERATION_ROUTES
    ):

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(cooldown)"
            )

            continue

        try:

            image = function(
                prompt
            )

        except Exception as exc:

            print(
                f"{name} ERROR:",
                exc
            )

            image = None

        if image:

            print(
                "IMAGE GENERATION SUCCESS:",
                name
            )

            return {

                "answer":
                    "تم إنشاء الصورة "
                    "بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    name
            }

        print(
            f"{name} failed. "
            "Trying next image provider..."
        )

    return {

        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة مزودي الصور "
            "المتاحين.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# IMAGE EDIT ROUTER
# ============================================================

IMAGE_EDIT_ROUTES = [

    (
        "XAI_EDIT",
        edit_image_xai
    ),

    (
        "OPENROUTER_IMAGE_EDIT",
        generate_image_openrouter
    )
]


def edit_image(
    prompt,
    image_bytes,
    mime_type,
    conversation_id=None
):

    """
    Edit an existing image.

    IMPORTANT:
    Vision providers are NOT used as fake image editors.

    A vision model may describe the image, but an edit request
    must be sent to an actual image-edit capable endpoint.
    """

    if not image_bytes:

        return {
            "answer":
                "لم يتم إرسال صورة صالحة للتعديل.",

            "imageUrl":
                "",

            "provider":
                None
        }

    if not mime_type:

        mime_type = "image/jpeg"

    if not mime_type.startswith(
        "image/"
    ):

        return {
            "answer":
                "الملف المرسل ليس صورة صالحة.",

            "imageUrl":
                "",

            "provider":
                None
        }

    prompt = clean_answer(
        prompt
    )

    if not prompt:

        return {
            "answer":
                "اكتب التعديل الذي تريد "
                "إجراءه على الصورة.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)

    print(
        "IMAGE EDIT STARTED"
    )

    print(
        "EDIT PROMPT:",
        prompt
    )

    print(
        "IMAGE MIME:",
        mime_type
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes)
    )

    print("=" * 60)

    # --------------------------------------------------------
    # XAI: true image editing
    # --------------------------------------------------------

    if provider_available(
        "XAI_EDIT"
    ):

        image = edit_image_xai(

            prompt,

            image_bytes,

            mime_type
        )

        if image:

            print(
                "IMAGE EDIT SUCCESS: XAI_EDIT"
            )

            return {

                "answer":
                    "تم تعديل الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "XAI_EDIT"
            }

        print(
            "XAI_EDIT failed."
        )

    # --------------------------------------------------------
    # OpenRouter image-to-image
    # --------------------------------------------------------

    if provider_available(
        "OPENROUTER_IMAGE_EDIT"
    ):

        try:

            image = generate_image_openrouter(

                prompt,

                image_bytes,

                mime_type
            )

        except Exception as exc:

            print(
                "OPENROUTER IMAGE EDIT ERROR:",
                exc
            )

            image = None

        if image:

            print(
                "IMAGE EDIT SUCCESS:",
                "OPENROUTER_IMAGE_EDIT"
            )

            return {

                "answer":
                    "تم تعديل الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "OPENROUTER_IMAGE_EDIT"
            }

        print(
            "OPENROUTER_IMAGE_EDIT failed."
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT return a vision answer here.
    # That was the old bug.
    # --------------------------------------------------------

    return {

        "answer":
            "تعذر تعديل الصورة حاليًا. "
            "لم ينجح أي مزود متاح "
            "في تنفيذ عملية التعديل.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# UNIFIED IMAGE ENTRY POINT
# ============================================================

def get_image_response(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
):

    """
    Unified image endpoint used by app.py.

    It decides between:
        1. image editing
        2. image analysis
    """

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

    message = (
        str(message).strip()
        if message
        else ""
    )

    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    if is_image_edit_request(
        message,
        has_image=True
    ):

        result = edit_image(

            message,

            image_bytes,

            mime_type,

            conversation_id
        )

        # app.py currently expects IMAGE_URL:
        # for generated/edited images.
        if isinstance(
            result,
            dict
        ):

            image_url = result.get(
                "imageUrl"
            )

            if image_url:

                return (
                    "IMAGE_URL:"
                    + image_url
                )

            return result.get(
                "answer",
                "تعذر تعديل الصورة."
            )

        return result

    # --------------------------------------------------------
    # VISION / ANALYSIS
    # --------------------------------------------------------

    return analyze_image(

        message,

        image_bytes,

        mime_type,

        conversation_id
    )


# ============================================================
# COMPATIBILITY HELPERS
# ============================================================

def ask_vision(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
):

    return analyze_image(

        message,

        image_bytes,

        mime_type,

        conversation_id
    )


def create_image(
    prompt
):

    return generate_image(
        prompt
    )


def modify_image(
    prompt,
    image_bytes,
    mime_type,
    conversation_id=None
):

    return edit_image(

        prompt,

        image_bytes,

        mime_type,

        conversation_id
    )


# ============================================================
# STARTUP LOG
# ============================================================

print("=" * 60)

print(
    "BRAIN.PY LOADED"
)

print(
    "TEXT ROUTE:"
)

print(
    "GROQ -> MISTRAL -> OPENROUTER "
    "-> GEMINI -> XAI -> POLLINATIONS"
)

print(
    "VISION ROUTE:"
)

print(
    "GROQ -> MISTRAL -> OPENROUTER -> XAI"
)

print(
    "IMAGE GENERATION ROUTE:"
)

print(
    "XAI -> POLLINATIONS -> OPENROUTER"
)

print(
    "IMAGE EDIT ROUTE:"
)

print(
    "XAI -> OPENROUTER"
)

print(
    "UNIFIED ROUTER: READY"
)

print("=" * 60)