# brain.py
# =========================================================
# Ido AI - UNIFIED MULTI-MODAL AI BRAIN
#
# TEXT:
#   Groq -> Mistral -> OpenRouter -> Gemini -> xAI -> Pollinations
#
# VISION / IMAGE ANALYSIS:
#   Mistral Vision -> Groq Vision -> OpenRouter Vision
#   -> Gemini Vision -> xAI Vision
#
# IMAGE GENERATION:
#   xAI -> OpenRouter -> Pollinations
#
# IMAGE EDITING:
#   xAI -> OpenRouter
#
# IMPORTANT:
#   Every route has automatic fallback.
#
#   If provider #1 fails:
#       -> provider #2
#       -> provider #3
#       -> provider #4
#       -> ...
#
#   get_response() accepts conversation_id
#   get_image_response() accepts conversation_id
#
# =========================================================

import os
import base64
import time
import requests

from dotenv import load_dotenv


# =========================================================
# GEMINI SDK
# =========================================================

try:
    from google import genai
    from google.genai.types import HttpOptions
except Exception:
    genai = None
    HttpOptions = None


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


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


CIRCUIT_BREAK_SECONDS = int(
    os.getenv(
        "PROVIDER_COOLDOWN_SECONDS",
        "300"
    )
)


_provider_disabled_until = {}


# =========================================================
# PROVIDER CONTROL
# =========================================================

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
        f"{name}: TEMPORARILY SKIPPED "
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
        429
    ):
        disable_provider(
            name,
            f"HTTP {status_code}"
        )


# =========================================================
# GENERAL HELPERS
# =========================================================

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
            f"{provider}: BODY:",
            response.text[:1500]
        )

        return None


def extract_chat_content(
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

    message = (
        choices[0]
        .get(
            "message",
            {}
        )
    )

    content = message.get(
        "content"
    )

    if isinstance(
        content,
        list
    ):

        parts = []

        for item in content:

            if isinstance(
                item,
                dict
            ):

                text = item.get(
                    "text"
                )

                if text:
                    parts.append(
                        str(text)
                    )

        content = "\n".join(
            parts
        )

    return clean_answer(
        content
    )


def image_data_url(
    image_bytes,
    mime_type
):

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )

    return (
        f"data:{mime_type};base64,"
        f"{encoded}"
    )


def image_result_from_data(
    item
):

    if not isinstance(
        item,
        dict
    ):
        return None

    image_url = item.get(
        "url"
    )

    if image_url:
        return image_url

    b64 = item.get(
        "b64_json"
    )

    if b64:

        media_type = item.get(
            "mime_type",
            item.get(
                "media_type",
                "image/png"
            )
        )

        return (
            f"data:{media_type};base64,"
            f"{b64}"
        )

    return None


# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

ENABLE_GEMINI = os.getenv(
    "ENABLE_GEMINI",
    "false"
).lower() == "true"


gemini_client = None


if (
    ENABLE_GEMINI
    and GEMINI_API_KEY
    and genai
):

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=30000
            )
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

        text = str(
            exc
        )

        print(
            "Gemini ERROR:",
            text
        )

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


# =========================================================
# GROQ
# =========================================================

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
                            "user",

                        "content":
                            message
                    }
                ],

                "temperature":
                    0.7,

                "max_completion_tokens":
                    1024
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "Groq ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: connection failed."
        )

        return None

    except Exception as exc:

        print(
            "Groq ERROR:",
            exc
        )

        return None


# =========================================================
# MISTRAL
# =========================================================

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
                            "user",

                        "content":
                            message
                    }
                ],

                "temperature":
                    0.7,

                "max_tokens":
                    1024
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "Mistral response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "Mistral ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Mistral ERROR: connection failed."
        )

        return None

    except Exception as exc:

        print(
            "Mistral ERROR:",
            exc
        )

        return None


# =========================================================
# OPENROUTER
# =========================================================

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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "OpenRouter response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "OpenRouter ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "OpenRouter ERROR: connection failed."
        )

        return None

    except Exception as exc:

        print(
            "OpenRouter ERROR:",
            exc
        )

        return None


# =========================================================
# XAI / GROK
# =========================================================

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
            "Trying xAI / Grok..."
        )

        response = requests.post(
            XAI_URL,

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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "xAI response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "xAI ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "xAI ERROR: connection failed."
        )

        return None

    except Exception as exc:

        print(
            "xAI ERROR:",
            exc
        )

        return None


# =========================================================
# POLLINATIONS
# =========================================================

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

POLLINATIONS_CHAT_URL = (
    "https://gen.pollinations.ai/v1/"
    "chat/completions"
)

POLLINATIONS_TEXT_MODEL = os.getenv(
    "POLLINATIONS_TEXT_MODEL",
    "openai"
)

POLLINATIONS_IMAGE_MODEL = os.getenv(
    "POLLINATIONS_IMAGE_MODEL",
    "flux"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/image/"
)


if POLLINATIONS_API_KEY:

    print(
        "POLLINATIONS CLIENT: READY"
    )

    print(
        "POLLINATIONS TEXT MODEL:",
        POLLINATIONS_TEXT_MODEL
    )

    print(
        "POLLINATIONS IMAGE MODEL:",
        POLLINATIONS_IMAGE_MODEL
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

        answer = extract_chat_content(
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


# =========================================================
# IMAGE GENERATION - xAI
# =========================================================

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
            "XAI IMAGE GENERATION STARTED"
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

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        image = image_result_from_data(
            items[0]
        )

        if image:

            print(
                "XAI IMAGE: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "XAI IMAGE ERROR:",
            exc
        )

        return None


# =========================================================
# IMAGE GENERATION - OPENROUTER
# =========================================================

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
            "OPENROUTER IMAGE "
            "GENERATION STARTED"
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

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        image = image_result_from_data(
            items[0]
        )

        if image:

            print(
                "OPENROUTER IMAGE: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "OPENROUTER IMAGE ERROR:",
            exc
        )

        return None


# =========================================================
# IMAGE GENERATION - POLLINATIONS
# =========================================================

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
            "POLLINATIONS IMAGE "
            "GENERATION STARTED"
        )

        url = (
            POLLINATIONS_IMAGE_URL
            +
            requests.utils.quote(
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
                    1024,

                "n":
                    1
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

        encoded = base64.b64encode(
            response.content
        ).decode(
            "utf-8"
        )

        image_data = (
            f"data:{content_type};base64,"
            f"{encoded}"
        )

        print(
            "POLLINATIONS IMAGE: SUCCESS"
        )

        return image_data

    except Exception as exc:

        print(
            "Pollinations IMAGE ERROR:",
            exc
        )

        return None


# =========================================================
# IMAGE GENERATION ROUTER
# =========================================================

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
        "IMAGE PROMPT:",
        prompt
    )

    print("=" * 60)


    # =====================================================
    # 1. xAI
    # =====================================================

    image = generate_image_xai(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة xAI.",

            "imageUrl":
                image,

            "provider":
                "xAI"
        }


    print(
        "xAI image failed."
    )


    # =====================================================
    # 2. OpenRouter
    # =====================================================

    image = generate_image_openrouter(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة OpenRouter.",

            "imageUrl":
                image,

            "provider":
                "OpenRouter"
        }


    print(
        "OpenRouter image failed."
    )


    # =====================================================
    # 3. Pollinations
    # =====================================================

    image = generate_image_pollinations(
        prompt
    )

    if image:

        return {
            "answer":
                "تم إنشاء الصورة بنجاح بواسطة Pollinations.",

            "imageUrl":
                image,

            "provider":
                "Pollinations"
        }


    print(
        "ALL IMAGE PROVIDERS FAILED."
    )


    return {
        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة جميع مولدات الصور "
            "المتاحة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# =========================================================
# IMAGE EDITING - xAI
# =========================================================

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
            "XAI IMAGE EDIT STARTED"
        )

        source_image = image_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(
            XAI_EDIT_URL,

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

                "image": {
                    "url":
                        source_image,

                    "type":
                        "image_url"
                }
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI EDIT STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI EDIT RESPONSE:",
                response.text[:1500]
            )

            provider_failure(
                "XAI_EDIT",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "xAI EDIT"
        )

        if not data:
            return None

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        image = image_result_from_data(
            items[0]
        )

        if image:

            print(
                "XAI IMAGE EDIT: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "XAI IMAGE EDIT ERROR:",
            exc
        )

        return None


# =========================================================
# IMAGE EDITING - OPENROUTER
# =========================================================

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
        "OPENROUTER_EDIT"
    ):
        return None

    try:

        print(
            "OPENROUTER IMAGE EDIT STARTED"
        )

        source_image = image_data_url(
            image_bytes,
            mime_type
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
                    1,

                "input_references": [
                    source_image
                ]
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter EDIT STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter EDIT RESPONSE:",
                response.text[:1500]
            )

            provider_failure(
                "OPENROUTER_EDIT",
                response.status_code
            )

            return None

        data = request_json(
            response,
            "OpenRouter EDIT"
        )

        if not data:
            return None

        items = data.get(
            "data",
            []
        )

        if not items:
            return None

        image = image_result_from_data(
            items[0]
        )

        if image:

            print(
                "OPENROUTER IMAGE EDIT: SUCCESS"
            )

            return image

        return None

    except Exception as exc:

        print(
            "OPENROUTER IMAGE EDIT ERROR:",
            exc
        )

        return None


# =========================================================
# IMAGE EDITING ROUTER
# =========================================================

def edit_image(
    prompt,
    image_bytes,
    mime_type
):

    prompt = clean_answer(
        prompt
    )

    if not prompt:

        return {
            "answer":
                "اكتب التعديل الذي تريد "
                "إجراؤه على الصورة.",

            "imageUrl":
                "",

            "provider":
                None
        }

    if not image_bytes:

        return {
            "answer":
                "لم يتم إرسال صورة صالحة.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)

    print(
        "IMAGE EDITING STARTED"
    )

    print(
        "EDIT PROMPT:",
        prompt
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

    print("=" * 60)


    # =====================================================
    # 1. xAI
    # =====================================================

    image = edit_image_xai(
        prompt,
        image_bytes,
        mime_type
    )

    if image:

        return {
            "answer":
                "تم تعديل الصورة بنجاح بواسطة xAI.",

            "imageUrl":
                image,

            "provider":
                "xAI"
        }


    print(
        "xAI editing failed."
    )


    # =====================================================
    # 2. OpenRouter
    # =====================================================

    image = edit_image_openrouter(
        prompt,
        image_bytes,
        mime_type
    )

    if image:

        return {
            "answer":
                "تم تعديل الصورة بنجاح بواسطة OpenRouter.",

            "imageUrl":
                image,

            "provider":
                "OpenRouter"
        }


    print(
        "OpenRouter editing failed."
    )


    return {
        "answer":
            "تعذر تعديل الصورة حاليًا. "
            "تمت تجربة جميع مزودي تعديل الصور "
            "المتاحين.",

        "imageUrl":
            "",

        "provider":
            None
    }


# =========================================================
# IMAGE REQUEST DETECTION
# =========================================================

IMAGE_WORDS = [

    # Arabic generation
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

    # English generation
    "generate an image",
    "generate image",

    "create an image",
    "create image",

    "make an image",
    "make image",

    "draw an image",
    "draw image"
]


EDIT_WORDS = [

    # Arabic
    "عدل الصورة",
    "عدّل الصورة",
    "تعديل الصورة",

    "عدل هذه الصورة",
    "عدّل هذه الصورة",

    "غير الصورة",
    "غيّر الصورة",

    "تغيير الصورة",

    "غير لون",
    "غيّر لون",

    "اجعل السيارة",
    "خلي السيارة",

    "أضف إلى الصورة",
    "اضف الى الصورة",

    "احذف من الصورة",
    "امسح من الصورة",

    "بدل الصورة",
    "بدّل الصورة",

    # English
    "edit the image",
    "edit image",

    "edit this image",

    "modify the image",
    "modify image",

    "change the image",
    "change image",

    "change the color",

    "remove from the image",

    "add to the image"
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
        for word in IMAGE_WORDS
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
        for word in EDIT_WORDS
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

        "draw an image of"
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


# =========================================================
# QUICK RESPONSES
# =========================================================

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

    text = str(
        message
    ).lower()

    for key, value in (
        QUICK_RESPONSES.items()
    ):

        if key.lower() in text:
            return value

    return None


# =========================================================
# TEXT ROUTER
# =========================================================

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


def route_text(
    message
):

    print("=" * 60)

    print(
        "TEXT ROUTER STARTED"
    )

    print(
        "MESSAGE:",
        message
    )

    print("=" * 60)


    for name, function in TEXT_ROUTES:

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
                message
            )

        except Exception as exc:

            print(
                f"{name} ROUTE ERROR:",
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


    return None


# =========================================================
# MAIN TEXT ENTRY
# =========================================================
#
# IMPORTANT:
# conversation_id is accepted here so app.py and api.py
# can safely call:
#
# get_response(
#     message,
#     conversation_id=conversation_id
# )
#
# =========================================================

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


    print("=" * 60)

    print(
        "GET_RESPONSE"
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print(
        "MESSAGE:",
        original_message
    )

    print("=" * 60)


    # =====================================================
    # IMAGE GENERATION WITHOUT UPLOADED IMAGE
    # =====================================================

    if is_image_generation_request(
        original_message
    ):

        prompt = get_image_prompt(
            original_message
        )

        return generate_image(
            prompt
        )


    # =====================================================
    # QUICK RESPONSE
    # =====================================================

    quick = quick_response(
        original_message
    )

    if quick:

        return quick


    # =====================================================
    # NORMAL TEXT
    # =====================================================

    answer = route_text(
        original_message
    )


    if answer:

        return answer


    return (
        "أنا Ido AI، لكن جميع مزودي "
        "الذكاء الاصطناعي المتاحين "
        "فشلوا حاليًا. "
        "سيتم الانتقال تلقائيًا بين "
        "المزودين عند توفرهم."
    )


# =========================================================
# VISION HELPER
# =========================================================

def make_vision_payload(
    message,
    image_bytes,
    mime_type
):

    source_image = image_data_url(
        image_bytes,
        mime_type
    )

    return [

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
                    source_image
            }
        }
    ]


# =========================================================
# MISTRAL VISION
# =========================================================

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

                        "content":
                            make_vision_payload(
                                message,
                                image_bytes,
                                mime_type
                            )
                    }
                ],

                "max_tokens":
                    1024
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
                response.text[:1200]
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "MISTRAL VISION SUCCESS"
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Mistral Vision ERROR:",
            exc
        )

        return None


# =========================================================
# GROQ VISION
# =========================================================

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

                        "content":
                            make_vision_payload(
                                message,
                                image_bytes,
                                mime_type
                            )
                    }
                ],

                "max_completion_tokens":
                    1024
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
                response.text[:1200]
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "GROQ VISION SUCCESS"
            )

            return answer

        return None

    except Exception as exc:

        print(
            "Groq Vision ERROR:",
            exc
        )

        return None


# =========================================================
# OPENROUTER VISION
# =========================================================

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

                        "content":
                            make_vision_payload(
                                message,
                                image_bytes,
                                mime_type
                            )
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
                response.text[:1200]
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "OPENROUTER VISION SUCCESS"
            )

            return answer

        return None

    except Exception as exc:

        print(
            "OpenRouter Vision ERROR:",
            exc
        )

        return None


# =========================================================
# GEMINI VISION
# =========================================================

def ask_gemini_image(
    message,
    image_bytes,
    mime_type
):

    if not ENABLE_GEMINI:
        return None

    if gemini_client is None:
        return None

    if not image_bytes:
        return None

    if not provider_available(
        "GEMINI_VISION"
    ):
        return None

    try:

        print(
            "Trying Gemini Vision..."
        )

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        # Gemini SDK support varies by installed version.
        # We use the data URI as the image input.
        image_uri = (
            f"data:{mime_type};base64,"
            f"{encoded}"
        )

        contents = [
            {
                "text":
                    message
            },
            {
                "inline_data": {
                    "mime_type":
                        mime_type,

                    "data":
                        encoded
                }
            }
        ]

        try:

            response = (
                gemini_client
                .models
                .generate_content(
                    model=GEMINI_MODEL,
                    contents=contents
                )
            )

        except Exception:

            # Fallback for SDK versions that
            # expect a simpler input.
            response = (
                gemini_client
                .models
                .generate_content(
                    model=GEMINI_MODEL,
                    contents=[
                        message,
                        image_uri
                    ]
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
                "GEMINI VISION SUCCESS"
            )

            return answer

        return None

    except Exception as exc:

        text = str(
            exc
        )

        print(
            "Gemini Vision ERROR:",
            text
        )

        if (
            "429" in text
            or
            "RESOURCE_EXHAUSTED"
            in text
        ):

            disable_provider(
                "GEMINI_VISION",
                "quota exceeded"
            )

        return None


# =========================================================
# xAI VISION
# =========================================================

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

        source_image = image_data_url(
            image_bytes,
            mime_type
        )

        response = requests.post(
            XAI_URL,

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
                                        source_image
                                }
                            }
                        ]
                    }
                ],

                "temperature":
                    0.3
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
                response.text[:1200]
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

        answer = extract_chat_content(
            data
        )

        if answer:

            print(
                "XAI VISION SUCCESS"
            )

            return answer

        return None

    except Exception as exc:

        print(
            "xAI Vision ERROR:",
            exc
        )

        return None


# =========================================================
# VISION ROUTER
# =========================================================

VISION_ROUTES = [

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
        "GEMINI_VISION",
        ask_gemini_image
    ),

    (
        "XAI_VISION",
        ask_xai_image
    )
]


def analyze_image(
    message,
    image_bytes,
    mime_type
):

    if not image_bytes:

        return (
            "لم يتم إرسال صورة صالحة."
        )


    if not mime_type:

        mime_type = (
            "image/jpeg"
        )


    if not mime_type.startswith(
        "image/"
    ):

        return (
            "الملف المرسل ليس "
            "صورة صالحة."
        )


    if not message:

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها بالتفصيل."
        )


    message = str(
        message
    ).strip()


    print("=" * 60)

    print(
        "VISION ROUTER STARTED"
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print(
        "IMAGE MIME:",
        mime_type
    )

    print(
        "VISION QUESTION:",
        message
    )

    print("=" * 60)


    for name, function in VISION_ROUTES:

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
                f"{name} ERROR:",
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


# =========================================================
# UNIFIED IMAGE ENTRY
# =========================================================
#
# This function decides:
#
# 1. Is the user asking to EDIT the image?
#       -> EDIT ROUTER
#
# 2. Otherwise:
#       -> VISION ROUTER
#
# The conversation_id is accepted for compatibility
# with app.py and api.py.
#
# =========================================================

def get_image_response(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
):

    print("=" * 60)

    print(
        "GET_IMAGE_RESPONSE"
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print(
        "MESSAGE:",
        message
    )

    print("=" * 60)


    if not image_bytes:

        return (
            "لم يتم إرسال صورة صالحة."
        )


    if not mime_type:

        mime_type = (
            "image/jpeg"
        )


    if not mime_type.startswith(
        "image/"
    ):

        return (
            "الملف المرسل ليس "
            "صورة صالحة."
        )


    text = str(
        message or ""
    ).strip()


    if not text:

        text = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )


    # =====================================================
    # IMAGE EDITING
    # =====================================================

    if is_image_edit_request(
        text
    ):

        result = edit_image(
            text,
            image_bytes,
            mime_type
        )


        if (
            isinstance(
                result,
                dict
            )
            and
            result.get(
                "imageUrl"
            )
        ):

            # Compatibility with the current app.py
            # which checks for IMAGE_URL:
            return (
                "IMAGE_URL:"
                +
                str(
                    result.get(
                        "imageUrl"
                    )
                )
            )


        return (
            result.get(
                "answer",
                "تعذر تعديل الصورة حاليًا."
            )
            if isinstance(
                result,
                dict
            )
            else
            (
                result
                or
                "تعذر تعديل الصورة حاليًا."
            )
        )


    # =====================================================
    # IMAGE ANALYSIS
    # =====================================================

    return analyze_image(
        text,
        image_bytes,
        mime_type
    )


# =========================================================
# STARTUP INFORMATION
# =========================================================

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
    "MISTRAL -> GROQ -> OPENROUTER "
    "-> GEMINI -> XAI"
)

print(
    "IMAGE GENERATION ROUTE:"
)

print(
    "XAI -> OPENROUTER -> POLLINATIONS"
)

print(
    "IMAGE EDIT ROUTE:"
)

print(
    "XAI -> OPENROUTER"
)

print("=" * 60)