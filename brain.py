# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# PROVIDER ROUTING
#
# TEXT:
#     XAI
#       ↓
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# VISION:
#     XAI
#       ↓
#     MISTRAL
#       ↓
#     GROQ
#
# IMAGE GENERATION:
#     XAI
#       ↓
#     OPENROUTER
#       ↓
#     MISTRAL
#
# IMAGE EDITING:
#     XAI
#       ↓
#     OPENROUTER
#       ↓
#     MISTRAL
#
# IMPORTANT:
#     Groq currently provides image understanding / vision,
#     not an independent image-generation endpoint.
#
# ============================================================

import os
import time
import base64
import logging
import requests

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("IDO-AI")


# ============================================================
# ENVIRONMENT
# ============================================================

XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


# ============================================================
# MODELS
# ============================================================

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


GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "qwen/qwen3.6-27b"
)


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "x-ai/grok-imagine-image-quality"
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


# ============================================================
# SETTINGS
# ============================================================

MISTRAL_MAX_RETRIES = int(
    os.getenv("MISTRAL_MAX_RETRIES", "2")
)

MISTRAL_RETRY_BASE_SECONDS = float(
    os.getenv("MISTRAL_RETRY_BASE_SECONDS", "2")
)

AI_REQUEST_TIMEOUT = int(
    os.getenv("AI_REQUEST_TIMEOUT", "180")
)


# ============================================================
# URLS
# ============================================================

XAI_BASE_URL = "https://api.x.ai/v1"

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)

print(
    "XAI CLIENT:",
    "READY" if XAI_API_KEY else "NOT CONFIGURED"
)

print(
    "MISTRAL CLIENT:",
    "READY" if MISTRAL_API_KEY else "NOT CONFIGURED"
)

print(
    "GROQ CLIENT:",
    "READY" if GROQ_API_KEY else "NOT CONFIGURED"
)

print(
    "OPENROUTER CLIENT:",
    "READY" if OPENROUTER_API_KEY else "NOT CONFIGURED"
)

print(
    "GEMINI CLIENT:",
    "READY" if GEMINI_API_KEY else "NOT CONFIGURED"
)

print("=" * 70)

print("XAI TEXT MODEL:", XAI_TEXT_MODEL)
print("XAI VISION MODEL:", XAI_VISION_MODEL)
print("XAI IMAGE MODEL:", XAI_IMAGE_MODEL)

print("MISTRAL VISION MODEL:", MISTRAL_VISION_MODEL)
print("MISTRAL IMAGE MODEL:", MISTRAL_IMAGE_MODEL)

print("GROQ TEXT MODEL:", GROQ_TEXT_MODEL)
print("GROQ VISION MODEL:", GROQ_VISION_MODEL)

print("OPENROUTER TEXT MODEL:", OPENROUTER_TEXT_MODEL)
print("OPENROUTER IMAGE MODEL:", OPENROUTER_IMAGE_MODEL)

print("GEMINI TEXT MODEL:", GEMINI_TEXT_MODEL)

print("=" * 70)

print(
    "MISTRAL MAX RETRIES:",
    MISTRAL_MAX_RETRIES
)

print(
    "MISTRAL RETRY BASE SECONDS:",
    MISTRAL_RETRY_BASE_SECONDS
)

print(
    "AI REQUEST TIMEOUT:",
    AI_REQUEST_TIMEOUT
)

print("=" * 70)


# ============================================================
# HTTP HELPERS
# ============================================================

def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}


def request_json(
    method,
    url,
    headers=None,
    json_data=None,
    timeout=None,
    files=None,
    data=None
):
    timeout = timeout or AI_REQUEST_TIMEOUT

    response = requests.request(
        method=method,
        url=url,
        headers=headers or {},
        json=json_data,
        files=files,
        data=data,
        timeout=timeout
    )

    return response


# ============================================================
# XAI HEADERS
# ============================================================

def xai_headers():
    return {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }


# ============================================================
# GROQ HEADERS
# ============================================================

def groq_headers():
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }


# ============================================================
# OPENROUTER HEADERS
# ============================================================

def openrouter_headers():
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ido-ai-production.up.railway.app",
        "X-Title": "IDO AI"
    }


# ============================================================
# MISTRAL HEADERS
# ============================================================

def mistral_headers():
    return {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }


# ============================================================
# GEMINI HEADERS
# ============================================================

def gemini_headers():
    return {
        "Content-Type": "application/json"
    }


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def extract_openai_text(data):
    try:
        choices = data.get("choices", [])

        if not choices:
            return None

        message = choices[0].get("message", {})

        content = message.get("content")

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):

            parts = []

            for item in content:

                if isinstance(item, dict):

                    text = item.get("text")

                    if text:
                        parts.append(text)

            if parts:
                return "\n".join(parts).strip()

        return None

    except Exception:
        return None


# ============================================================
# XAI TEXT
# ============================================================

def xai_text(message):

    if not XAI_API_KEY:
        raise RuntimeError("XAI_API_KEY is missing")

    url = f"{XAI_BASE_URL}/chat/completions"

    payload = {
        "model": XAI_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Answer clearly and naturally. "
                    "If the user speaks Arabic or Moroccan Darija, "
                    "answer in Arabic/Darija when appropriate."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7
    }

    response = request_json(
        "POST",
        url,
        headers=xai_headers(),
        json_data=payload
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"xAI TEXT {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    result = extract_openai_text(data)

    if not result:
        raise RuntimeError("xAI returned empty text")

    return result


# ============================================================
# GROQ TEXT
# ============================================================

def groq_text(message):

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing")

    url = f"{GROQ_BASE_URL}/chat/completions"

    payload = {
        "model": GROQ_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Give accurate and useful answers."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7
    }

    response = request_json(
        "POST",
        url,
        headers=groq_headers(),
        json_data=payload
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Groq TEXT {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    result = extract_openai_text(data)

    if not result:
        raise RuntimeError("Groq returned empty text")

    return result


# ============================================================
# OPENROUTER TEXT
# ============================================================

def openrouter_text(message):

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing"
        )

    url = f"{OPENROUTER_BASE_URL}/chat/completions"

    payload = {
        "model": OPENROUTER_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are IDO AI."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    response = request_json(
        "POST",
        url,
        headers=openrouter_headers(),
        json_data=payload
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenRouter TEXT {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    result = extract_openai_text(data)

    if not result:
        raise RuntimeError(
            "OpenRouter returned empty text"
        )

    return result


# ============================================================
# GEMINI TEXT
# ============================================================

def gemini_text(message):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing"
        )

    url = (
        f"{GEMINI_BASE_URL}/models/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }

    response = request_json(
        "POST",
        url,
        headers=gemini_headers(),
        json_data=payload
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Gemini TEXT {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    candidates = data.get("candidates", [])

    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates"
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    texts = []

    for part in parts:

        text = part.get("text")

        if text:
            texts.append(text)

    result = "\n".join(texts).strip()

    if not result:
        raise RuntimeError(
            "Gemini returned empty text"
        )

    return result


# ============================================================
# FINAL TEXT ROUTING
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    print("=" * 70)
    print("TEXT REQUEST")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    providers = [
        ("xAI", xai_text),
        ("Groq", groq_text),
        ("OpenRouter", openrouter_text),
        ("Gemini", gemini_text)
    ]

    errors = []

    for name, provider in providers:

        try:

            print("TEXT PROVIDER:", name)

            answer = provider(message)

            if answer:

                print("TEXT SUCCESS:", name)

                return answer

        except Exception as exc:

            error = f"{name}: {exc}"

            errors.append(error)

            print(
                "TEXT PROVIDER ERROR:",
                error
            )

    print("=" * 70)

    return (
        "عذرًا، تعذر الحصول على إجابة من مزودي الذكاء الاصطناعي حاليًا."
    )


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(message):

    return get_response(message)


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
            "XAI_API_KEY is missing"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    url = f"{XAI_BASE_URL}/chat/completions"

    payload = {
        "model": XAI_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ]
    }

    response = request_json(
        "POST",
        url,
        headers=xai_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"xAI VISION {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    result = extract_openai_text(data)

    if not result:

        raise RuntimeError(
            "xAI vision returned empty response"
        )

    return result


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
            "MISTRAL_API_KEY is missing"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    url = (
        f"{MISTRAL_BASE_URL}/chat/completions"
    )

    payload = {
        "model": MISTRAL_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ]
    }

    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        try:

            print(
                f"MISTRAL VISION ATTEMPT: "
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}"
            )

            response = request_json(
                "POST",
                url,
                headers=mistral_headers(),
                json_data=payload
            )

            if response.status_code == 429:

                if attempt >= MISTRAL_MAX_RETRIES:

                    raise RuntimeError(
                        "Mistral vision rate limit"
                    )

                delay = (
                    MISTRAL_RETRY_BASE_SECONDS
                    * (2 ** attempt)
                )

                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )

                if retry_after:

                    try:
                        delay = float(
                            retry_after
                        )
                    except Exception:
                        pass

                time.sleep(
                    min(delay, 30)
                )

                continue

            if response.status_code >= 400:

                raise RuntimeError(
                    f"Mistral VISION "
                    f"{response.status_code}: "
                    f"{response.text[:1000]}"
                )

            data = safe_json(response)

            result = extract_openai_text(data)

            if result:
                return result

            raise RuntimeError(
                "Mistral vision returned empty response"
            )

        except Exception:

            if attempt >= MISTRAL_MAX_RETRIES:
                raise

            delay = (
                MISTRAL_RETRY_BASE_SECONDS
                * (2 ** attempt)
            )

            time.sleep(
                min(delay, 30)
            )

    raise RuntimeError(
        "Mistral vision failed"
    )


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
            "GROQ_API_KEY is missing"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    url = (
        f"{GROQ_BASE_URL}/chat/completions"
    )

    payload = {
        "model": GROQ_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ]
    }

    response = request_json(
        "POST",
        url,
        headers=groq_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"Groq VISION "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = safe_json(response)

    result = extract_openai_text(data)

    if not result:

        raise RuntimeError(
            "Groq vision returned empty response"
        )

    return result


# ============================================================
# FINAL VISION ROUTING
# ============================================================

def analyze_image(
    message,
    image_bytes,
    mime_type
):

    print("=" * 70)
    print("IMAGE UNDERSTANDING")
    print("=" * 70)

    providers = [
        ("xAI Vision", xai_vision),
        ("Mistral Vision", mistral_vision),
        ("Groq Vision", groq_vision)
    ]

    for name, provider in providers:

        try:

            print(
                "VISION PROVIDER:",
                name
            )

            result = provider(
                message,
                image_bytes,
                mime_type
            )

            if result:

                print(
                    "VISION SUCCESS:",
                    name
                )

                return result

        except Exception as exc:

            print(
                "VISION ERROR:",
                name,
                exc
            )

    return (
        "تعذر تحليل الصورة حاليًا."
    )


# ============================================================
# XAI IMAGE GENERATION
# ============================================================

def xai_image_generate(prompt):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing"
        )

    print("=" * 70)
    print("XAI IMAGE GENERATION")
    print("=" * 70)

    print(
        "MODEL:",
        XAI_IMAGE_MODEL
    )

    url = (
        f"{XAI_BASE_URL}/images/generations"
    )

    payload = {
        "model": XAI_IMAGE_MODEL,
        "prompt": prompt,
        "response_format": "url"
    }

    response = request_json(
        "POST",
        url,
        headers=xai_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"xAI IMAGE "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    data = safe_json(response)

    items = data.get("data", [])

    if not items:

        raise RuntimeError(
            "xAI returned no image"
        )

    item = items[0]

    image_url = item.get("url")

    if image_url:

        return {
            "success": True,
            "provider": "xAI",
            "image_url": image_url,
            "url": image_url
        }

    b64 = item.get("b64_json")

    if b64:

        return {
            "success": True,
            "provider": "xAI",
            "image_base64": b64,
            "b64_json": b64
        }

    raise RuntimeError(
        "xAI image response contains no URL or base64"
    )


# ============================================================
# OPENROUTER IMAGE GENERATION
# ============================================================

def openrouter_image_generate(prompt):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing"
        )

    print("=" * 70)
    print("OPENROUTER IMAGE GENERATION")
    print("=" * 70)

    print(
        "MODEL:",
        OPENROUTER_IMAGE_MODEL
    )

    url = (
        f"{OPENROUTER_BASE_URL}/images"
    )

    payload = {
        "model": OPENROUTER_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1
    }

    response = request_json(
        "POST",
        url,
        headers=openrouter_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"OpenRouter IMAGE "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    data = safe_json(response)

    items = data.get("data", [])

    if not items:

        raise RuntimeError(
            "OpenRouter returned no image"
        )

    item = items[0]

    image_url = item.get("url")

    if image_url:

        return {
            "success": True,
            "provider": "OpenRouter",
            "image_url": image_url,
            "url": image_url
        }

    b64 = item.get("b64_json")

    if b64:

        return {
            "success": True,
            "provider": "OpenRouter",
            "image_base64": b64,
            "b64_json": b64
        }

    media_type = item.get(
        "media_type",
        "image/png"
    )

    if isinstance(
        item.get("image_url"),
        dict
    ):

        image_url = item[
            "image_url"
        ].get("url")

        if image_url:

            return {
                "success": True,
                "provider": "OpenRouter",
                "image_url": image_url,
                "url": image_url
            }

    raise RuntimeError(
        "OpenRouter image response "
        "contains no usable image"
    )


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def mistral_image_generate(prompt):

    if not MISTRAL_API_KEY:

        raise RuntimeError(
            "MISTRAL_API_KEY is missing"
        )

    print("=" * 70)
    print("MISTRAL IMAGE GENERATION")
    print("=" * 70)

    print(
        "MODEL:",
        MISTRAL_IMAGE_MODEL
    )

    url = (
        f"{MISTRAL_BASE_URL}/chat/completions"
    )

    payload = {
        "model": MISTRAL_IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Generate an image based on "
                    "this request:\n\n"
                    + prompt
                )
            }
        ],
        "tools": [
            {
                "type": "image_generation"
            }
        ]
    }

    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        print(
            "MISTRAL REQUEST ATTEMPT:",
            f"{attempt + 1}/"
            f"{MISTRAL_MAX_RETRIES + 1}"
        )

        try:

            response = request_json(
                "POST",
                url,
                headers=mistral_headers(),
                json_data=payload
            )

            if response.status_code == 429:

                if attempt >= MISTRAL_MAX_RETRIES:

                    raise RuntimeError(
                        "Mistral image rate limit"
                    )

                delay = (
                    MISTRAL_RETRY_BASE_SECONDS
                    * (2 ** attempt)
                )

                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )

                if retry_after:

                    try:
                        delay = float(
                            retry_after
                        )
                    except Exception:
                        pass

                time.sleep(
                    min(delay, 30)
                )

                continue

            if response.status_code >= 400:

                raise RuntimeError(
                    f"Mistral IMAGE "
                    f"{response.status_code}: "
                    f"{response.text[:1500]}"
                )

            data = safe_json(response)

            image_url = find_image_url(
                data
            )

            if image_url:

                return {
                    "success": True,
                    "provider": "Mistral",
                    "image_url": image_url,
                    "url": image_url
                }

            raise RuntimeError(
                "Mistral did not return "
                "a generated image URL"
            )

        except Exception:

            if attempt >= MISTRAL_MAX_RETRIES:
                raise

            delay = (
                MISTRAL_RETRY_BASE_SECONDS
                * (2 ** attempt)
            )

            time.sleep(
                min(delay, 30)
            )

    raise RuntimeError(
        "Mistral image generation failed"
    )


# ============================================================
# FIND IMAGE URL INSIDE MISTRAL RESPONSE
# ============================================================

def find_image_url(data):

    if not isinstance(
        data,
        dict
    ):
        return None

    # --------------------------------------------------------
    # Direct data URL
    # --------------------------------------------------------

    direct = data.get("url")

    if isinstance(
        direct,
        str
    ) and direct.startswith(
        "http"
    ):

        return direct

    # --------------------------------------------------------
    # choices
    # --------------------------------------------------------

    choices = data.get(
        "choices",
        []
    )

    for choice in choices:

        if not isinstance(
            choice,
            dict
        ):
            continue

        message = choice.get(
            "message",
            {}
        )

        # ----------------------------------------------------
        # message content
        # ----------------------------------------------------

        content = message.get(
            "content"
        )

        if isinstance(
            content,
            str
        ):

            found = extract_url(
                content
            )

            if found:
                return found

        # ----------------------------------------------------
        # content list
        # ----------------------------------------------------

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

                for key in (
                    "url",
                    "image_url"
                ):

                    value = item.get(
                        key
                    )

                    if isinstance(
                        value,
                        dict
                    ):

                        value = value.get(
                            "url"
                        )

                    if (
                        isinstance(
                            value,
                            str
                        )
                        and
                        value.startswith(
                            "http"
                        )
                    ):

                        return value

        # ----------------------------------------------------
        # choices.messages
        # ----------------------------------------------------

        messages = choice.get(
            "messages",
            []
        )

        if isinstance(
            messages,
            list
        ):

            for msg in messages:

                if not isinstance(
                    msg,
                    dict
                ):
                    continue

                msg_content = msg.get(
                    "content"
                )

                if isinstance(
                    msg_content,
                    list
                ):

                    for item in msg_content:

                        if not isinstance(
                            item,
                            dict
                        ):
                            continue

                        for key in (
                            "url",
                            "image_url"
                        ):

                            value = item.get(
                                key
                            )

                            if isinstance(
                                value,
                                dict
                            ):

                                value = value.get(
                                    "url"
                                )

                            if (
                                isinstance(
                                    value,
                                    str
                                )
                                and
                                value.startswith(
                                    "http"
                                )
                            ):

                                return value

    return None


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_url(text):

    if not isinstance(
        text,
        str
    ):
        return None

    for token in text.split():

        token = (
            token
            .strip(
                "\"'()[]<>"
            )
        )

        if token.startswith(
            "https://"
        ):

            if (
                ".png" in token
                or ".jpg" in token
                or ".jpeg" in token
                or ".webp" in token
                or "files.mistral.ai" in token
            ):

                return token

    return None


# ============================================================
# IMAGE GENERATION ROUTER
# ============================================================

def generate_image(
    prompt,
    image_bytes=None,
    mime_type=None
):

    print("=" * 70)
    print("IMAGE GENERATION START")
    print("=" * 70)

    print(
        "PROMPT:",
        prompt
    )

    print(
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )

    errors = []

    # ========================================================
    # 1. XAI
    # ========================================================

    try:

        if image_bytes:

            return xai_image_edit(
                prompt,
                image_bytes,
                mime_type
            )

        return xai_image_generate(
            prompt
        )

    except Exception as exc:

        print(
            "xAI IMAGE ERROR:",
            exc
        )

        errors.append(
            f"xAI: {exc}"
        )


    # ========================================================
    # 2. OPENROUTER
    # ========================================================

    try:

        if image_bytes:

            result = (
                openrouter_image_edit(
                    prompt,
                    image_bytes,
                    mime_type
                )
            )

            if result:
                return result

        else:

            return openrouter_image_generate(
                prompt
            )

    except Exception as exc:

        print(
            "OPENROUTER IMAGE ERROR:",
            exc
        )

        errors.append(
            f"OpenRouter: {exc}"
        )


    # ========================================================
    # 3. MISTRAL
    # ========================================================

    try:

        if not image_bytes:

            return mistral_image_generate(
                prompt
            )

    except Exception as exc:

        print(
            "MISTRAL IMAGE ERROR:",
            exc
        )

        errors.append(
            f"Mistral: {exc}"
        )


    # ========================================================
    # GROQ
    # ========================================================
    #
    # Groq is intentionally NOT called as an image generator.
    #
    # Groq's current image API support is vision/image-input,
    # not independent image generation.
    #
    # Therefore calling a fake Groq image endpoint would create
    # exactly the kind of failure we are trying to eliminate.
    #
    # ========================================================

    print(
        "GROQ IMAGE:",
        "VISION ONLY - NO IMAGE GENERATION ENDPOINT"
    )


    print("=" * 70)
    print(
        "ALL IMAGE PROVIDERS FAILED"
    )
    print("=" * 70)

    return {
        "success": False,
        "provider": None,
        "error": " | ".join(errors)
    }


# ============================================================
# XAI IMAGE EDIT
# ============================================================

def xai_image_edit(
    prompt,
    image_bytes,
    mime_type
):

    if not XAI_API_KEY:

        raise RuntimeError(
            "XAI_API_KEY is missing"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    url = (
        f"{XAI_BASE_URL}/images/edits"
    )

    payload = {
        "model": XAI_IMAGE_MODEL,
        "prompt": prompt,
        "image": {
            "url": image_data,
            "type": "image_url"
        },
        "response_format": "url"
    }

    response = request_json(
        "POST",
        url,
        headers=xai_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"xAI IMAGE EDIT "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    data = safe_json(response)

    items = data.get(
        "data",
        []
    )

    if not items:

        raise RuntimeError(
            "xAI returned no edited image"
        )

    item = items[0]

    image_url = item.get(
        "url"
    )

    if image_url:

        return {
            "success": True,
            "provider": "xAI",
            "image_url": image_url,
            "url": image_url,
            "edited": True
        }

    b64 = item.get(
        "b64_json"
    )

    if b64:

        return {
            "success": True,
            "provider": "xAI",
            "image_base64": b64,
            "b64_json": b64,
            "edited": True
        }

    raise RuntimeError(
        "xAI edit returned no usable image"
    )


# ============================================================
# OPENROUTER IMAGE EDIT
# ============================================================

def openrouter_image_edit(
    prompt,
    image_bytes,
    mime_type
):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    url = (
        f"{OPENROUTER_BASE_URL}/images"
    )

    payload = {
        "model": OPENROUTER_IMAGE_MODEL,
        "prompt": prompt,
        "images": [
            image_data
        ],
        "n": 1
    }

    response = request_json(
        "POST",
        url,
        headers=openrouter_headers(),
        json_data=payload
    )

    if response.status_code >= 400:

        raise RuntimeError(
            f"OpenRouter IMAGE EDIT "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    data = safe_json(response)

    items = data.get(
        "data",
        []
    )

    if not items:

        raise RuntimeError(
            "OpenRouter returned no edited image"
        )

    item = items[0]

    image_url = item.get(
        "url"
    )

    if image_url:

        return {
            "success": True,
            "provider": "OpenRouter",
            "image_url": image_url,
            "url": image_url,
            "edited": True
        }

    b64 = item.get(
        "b64_json"
    )

    if b64:

        return {
            "success": True,
            "provider": "OpenRouter",
            "image_base64": b64,
            "b64_json": b64,
            "edited": True
        }

    raise RuntimeError(
        "OpenRouter edit returned no usable image"
    )


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

IMAGE_KEYWORDS = [
    "انشئ صورة",
    "أنشئ صورة",
    "اصنع صورة",
    "إصنع صورة",
    "اعمل صورة",
    "صمم صورة",
    "صورة ل",
    "صوره ل",
    "صورة عن",
    "صوره عن",
    "ولد صورة",
    "توليد صورة",
    "إنشاء صورة",
    "انشاء صورة",
    "generate image",
    "generate a picture",
    "create image",
    "create a picture",
    "make an image",
    "make a picture",
    "draw",
    "create a photo",
    "generate a photo"
]


def is_image_request(message):

    if not message:
        return False

    text = str(message).lower().strip()

    return any(
        keyword.lower() in text
        for keyword in IMAGE_KEYWORDS
    )


# ============================================================
# REMOVE IMAGE COMMAND
# ============================================================

def clean_image_prompt(message):

    if not message:
        return ""

    text = str(message).strip()

    prefixes = [
        "انشئ صورة",
        "أنشئ صورة",
        "اصنع صورة",
        "إصنع صورة",
        "اعمل صورة",
        "صمم صورة",
        "صورة ل",
        "صوره ل",
        "صورة عن",
        "صوره عن",
        "توليد صورة",
        "إنشاء صورة",
        "انشاء صورة",
        "generate image",
        "generate a picture",
        "create image",
        "create a picture",
        "make an image",
        "make a picture"
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
# COMPATIBILITY IMAGE FUNCTION
# ============================================================

def get_image_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

    print("=" * 70)
    print("IMAGE REQUEST")
    print("=" * 70)

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

    prompt = clean_image_prompt(
        message
    )

    print(
        "CLEAN IMAGE PROMPT:",
        prompt
    )

    result = generate_image(
        prompt,
        image_bytes=image_bytes,
        mime_type=mime_type
    )

    if not result:

        return {
            "success": False,
            "error": "No image result"
        }

    return result


# ============================================================
# DYNAMIC RESPONSE
# ============================================================

def dynamic_response(
    message,
    image_bytes=None,
    mime_type=None,
    conversation_id=None
):

    print("=" * 70)
    print("DYNAMIC AI RESPONSE")
    print(
        "MESSAGE:",
        message
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 70)

    # --------------------------------------------------------
    # IMAGE REQUEST
    # --------------------------------------------------------

    if (
        image_bytes
        or is_image_request(message)
    ):

        print(
            "IMAGE REQUEST DETECTED"
        )

        return get_image_response(
            message,
            image_bytes,
            mime_type,
            conversation_id
        )

    # --------------------------------------------------------
    # NORMAL TEXT
    # --------------------------------------------------------

    return {
        "success": True,
        "type": "text",
        "text": get_response(
            message,
            conversation_id
        )
    }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

ask_ai = get_response
chat = get_response
respond = dynamic_response


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
      ↓
    GROQ VISION
""")

print("""
IMAGE GENERATION:
    XAI
      ↓
    OPENROUTER
      ↓
    MISTRAL
""")

print("""
IMAGE EDITING:
    XAI
      ↓
    OPENROUTER
""")

print("""
GROQ:
    TEXT
    VISION
    IMAGE UNDERSTANDING

    IMAGE GENERATION:
    NOT AVAILABLE AS A GROQ NATIVE ENDPOINT
""")

print("""
XAI:
    TEXT
    VISION
    IMAGE GENERATION
    IMAGE EDITING
""")

print("""
OPENROUTER:
    TEXT
    IMAGE GENERATION
    IMAGE EDITING
""")

print("""
MISTRAL:
    VISION
    IMAGE GENERATION TOOL
""")

print("=" * 70)
print(
    "COMPATIBILITY: quick_response available"
)
print(
    "COMPATIBILITY: "
    "get_response(message, conversation_id=None)"
)
print(
    "COMPATIBILITY: "
    "get_image_response(message, image_bytes, mime_type, conversation_id=None)"
)
print("=" * 70)
print("IDO AI BRAIN.PY READY")
print("=" * 70)