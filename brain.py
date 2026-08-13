# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL PROVIDER ROUTING
#
# TEXT:
#     XAI
#       ↓
#     MISTRAL
#       ↓
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# IMAGE UNDERSTANDING:
#     XAI VISION
#       ↓
#     MISTRAL VISION
#       ↓
#     GROQ VISION
#
# IMAGE GENERATION:
#     XAI IMAGE
#       ↓
#     OPENROUTER IMAGE
#       ↓
#     MISTRAL IMAGE
#
# IMAGE EDITING:
#     XAI IMAGE EDIT
#       ↓
#     OPENROUTER IMAGE
#       ↓
#     MISTRAL IMAGE
#
# IMPORTANT:
#     Groq API currently provides image INPUT / VISION,
#     but does not provide native image OUTPUT generation.
#
#     Therefore Groq is used for vision and text fallback,
#     while OpenRouter is the real image-generation fallback.
#
# ============================================================

import os
import time
import base64
import logging
from typing import Optional, Any

import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | IDO AI | %(levelname)s | %(message)s",
)

logger = logging.getLogger("IDO_AI")


# ============================================================
# API KEYS
# ============================================================

XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    os.getenv("OPEN_ROUTER_API_KEY", "")
).strip()

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


MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
)

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
)


GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "qwen/qwen3.6-27b"
)

# Compatibility only.
# Groq has no native image-generation endpoint.
GROQ_IMAGE_MODEL = os.getenv(
    "GROQ_IMAGE_MODEL",
    ""
)


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "google/gemini-2.5-flash-image"
)


GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash"
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
# ENDPOINTS
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
    "READY" if XAI_API_KEY else "DISABLED"
)

print(
    "MISTRAL CLIENT:",
    "READY" if MISTRAL_API_KEY else "DISABLED"
)

print(
    "GROQ CLIENT:",
    "READY" if GROQ_API_KEY else "DISABLED"
)

print(
    "OPENROUTER CLIENT:",
    "READY" if OPENROUTER_API_KEY else "DISABLED"
)

print(
    "GEMINI CLIENT:",
    "READY" if GEMINI_API_KEY else "DISABLED"
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
print("MISTRAL MAX RETRIES:", MISTRAL_MAX_RETRIES)
print(
    "MISTRAL RETRY BASE SECONDS:",
    MISTRAL_RETRY_BASE_SECONDS
)
print("AI REQUEST TIMEOUT:", AI_REQUEST_TIMEOUT)

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
      ↓
    GROQ VISION
""")

print("""
IMAGE GENERATION:
    XAI IMAGE
      ↓
    OPENROUTER IMAGE
      ↓
    MISTRAL IMAGE
""")

print("""
IMAGE EDITING:
    XAI IMAGE EDIT
      ↓
    OPENROUTER IMAGE
      ↓
    MISTRAL IMAGE
""")

print("=" * 70)


# ============================================================
# HTTP HELPERS
# ============================================================

def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _post(
    url: str,
    headers: dict,
    payload: dict,
    timeout: Optional[int] = None,
):
    timeout = timeout or AI_REQUEST_TIMEOUT

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=timeout,
    )

    return response


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}


def _extract_text(data: Any) -> str:
    """
    Extract text from several OpenAI-compatible APIs.
    """

    if not isinstance(data, dict):
        return ""

    # --------------------------------------------------------
    # OpenAI / Groq / xAI style
    # --------------------------------------------------------

    choices = data.get("choices")

    if isinstance(choices, list) and choices:

        choice = choices[0]

        message = choice.get("message", {})

        if isinstance(message, dict):

            content = message.get("content")

            if isinstance(content, str):
                return content.strip()

            if isinstance(content, list):

                parts = []

                for item in content:

                    if isinstance(item, dict):

                        text = item.get("text")

                        if text:
                            parts.append(str(text))

                if parts:
                    return "\n".join(parts).strip()

        text = choice.get("text")

        if isinstance(text, str):
            return text.strip()

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    candidates = data.get("candidates")

    if isinstance(candidates, list) and candidates:

        candidate = candidates[0]

        content = candidate.get("content", {})

        if isinstance(content, dict):

            parts = content.get("parts", [])

            if isinstance(parts, list):

                result = []

                for part in parts:

                    if isinstance(part, dict):

                        text = part.get("text")

                        if text:
                            result.append(str(text))

                if result:
                    return "\n".join(result).strip()

    # --------------------------------------------------------
    # Mistral alternate structures
    # --------------------------------------------------------

    if "output_text" in data:

        text = data.get("output_text")

        if isinstance(text, str):
            return text.strip()

    return ""


# ============================================================
# IMAGE URL EXTRACTION
# ============================================================

def _extract_image_url(data: Any) -> Optional[str]:
    """
    Extract generated image URL from xAI / Mistral responses.
    """

    if not isinstance(data, dict):
        return None

    # --------------------------------------------------------
    # xAI / OpenAI image response
    # --------------------------------------------------------

    items = data.get("data")

    if isinstance(items, list):

        for item in items:

            if not isinstance(item, dict):
                continue

            url = item.get("url")

            if isinstance(url, str) and url:
                return url

            public_url = item.get("public_url")

            if isinstance(public_url, str) and public_url:
                return public_url

            b64 = item.get("b64_json")

            if isinstance(b64, str) and b64:

                return (
                    "data:image/png;base64,"
                    + b64
                )

    # --------------------------------------------------------
    # Mistral nested content
    # --------------------------------------------------------

    def recursive_find(obj):

        if isinstance(obj, str):

            if obj.startswith("http://"):
                return obj

            if obj.startswith("https://"):
                return obj

            return None

        if isinstance(obj, dict):

            for key in (
                "url",
                "image_url",
                "public_url",
                "file_url",
            ):

                value = obj.get(key)

                if isinstance(value, str):

                    if value.startswith("http://"):
                        return value

                    if value.startswith("https://"):
                        return value

            for value in obj.values():

                found = recursive_find(value)

                if found:
                    return found

        elif isinstance(obj, list):

            for value in obj:

                found = recursive_find(value)

                if found:
                    return found

        return None

    return recursive_find(data)


# ============================================================
# IMAGE BYTES -> DATA URL
# ============================================================

def _image_to_data_url(
    image_bytes: bytes,
    mime_type: Optional[str],
) -> str:

    mime_type = mime_type or "image/png"

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ============================================================
# XAI TEXT
# ============================================================

def _xai_text(message: str) -> Optional[str]:

    if not XAI_API_KEY:
        return None

    print("TEXT PROVIDER: XAI")

    payload = {
        "model": XAI_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Answer naturally and accurately. "
                    "You can communicate in Arabic, "
                    "Moroccan Darija, French and English."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    }

    try:

        response = _post(
            f"{XAI_BASE_URL}/chat/completions",
            _headers(XAI_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "XAI TEXT ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        text = _extract_text(
            response.json()
        )

        if text:
            return text

    except Exception as exc:

        print("XAI TEXT EXCEPTION:", exc)

    return None


# ============================================================
# MISTRAL TEXT
# ============================================================

def _mistral_text(message: str) -> Optional[str]:

    if not MISTRAL_API_KEY:
        return None

    print("TEXT PROVIDER: MISTRAL")

    payload = {
        "model": MISTRAL_IMAGE_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Answer naturally and accurately. "
                    "Use the language of the user."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        "max_tokens": 4096,
    }

    # Use vision model only for image-related requests.
    payload["model"] = os.getenv(
        "MISTRAL_TEXT_MODEL",
        "mistral-medium-latest"
    )

    try:

        for attempt in range(
            MISTRAL_MAX_RETRIES + 1
        ):

            print(
                f"MISTRAL REQUEST ATTEMPT: "
                f"{attempt + 1}/{MISTRAL_MAX_RETRIES + 1}"
            )

            response = _post(
                f"{MISTRAL_BASE_URL}/chat/completions",
                _headers(MISTRAL_API_KEY),
                payload,
            )

            if response.status_code == 429:

                if attempt >= MISTRAL_MAX_RETRIES:
                    return None

                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:

                    try:
                        delay = float(retry_after)
                    except Exception:
                        delay = (
                            MISTRAL_RETRY_BASE_SECONDS
                            * (2 ** attempt)
                        )

                else:

                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        * (2 ** attempt)
                    )

                delay = min(delay, 30)

                print(
                    "MISTRAL RATE LIMIT - "
                    f"sleeping {delay}s"
                )

                time.sleep(delay)

                continue

            if response.status_code >= 400:

                print(
                    "MISTRAL TEXT ERROR:",
                    response.status_code,
                    response.text[:500],
                )

                return None

            text = _extract_text(
                response.json()
            )

            if text:
                return text

            return None

    except Exception as exc:

        print(
            "MISTRAL TEXT EXCEPTION:",
            exc
        )

    return None


# ============================================================
# GROQ TEXT
# ============================================================

def _groq_text(message: str) -> Optional[str]:

    if not GROQ_API_KEY:
        return None

    print("TEXT PROVIDER: GROQ")

    payload = {
        "model": GROQ_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Answer naturally and accurately. "
                    "Use the user's language."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    }

    try:

        response = _post(
            f"{GROQ_BASE_URL}/chat/completions",
            _headers(GROQ_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "GROQ TEXT ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "GROQ TEXT EXCEPTION:",
            exc
        )

        return None


# ============================================================
# OPENROUTER TEXT
# ============================================================

def _openrouter_text(message: str) -> Optional[str]:

    if not OPENROUTER_API_KEY:
        return None

    print("TEXT PROVIDER: OPENROUTER")

    payload = {
        "model": OPENROUTER_TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are IDO AI. "
                    "Answer naturally and accurately. "
                    "Use the user's language."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    }

    try:

        response = _post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            _headers(OPENROUTER_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "OPENROUTER TEXT ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "OPENROUTER TEXT EXCEPTION:",
            exc
        )

        return None


# ============================================================
# GEMINI TEXT
# ============================================================

def _gemini_text(message: str) -> Optional[str]:

    if not GEMINI_API_KEY:
        return None

    print("TEXT PROVIDER: GEMINI")

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
                ],
            }
        ]
    }

    try:

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=AI_REQUEST_TIMEOUT,
        )

        if response.status_code >= 400:

            print(
                "GEMINI ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "GEMINI EXCEPTION:",
            exc
        )

        return None


# ============================================================
# XAI VISION
# ============================================================

def _xai_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not XAI_API_KEY:
        return None

    print("VISION PROVIDER: XAI")

    image_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )

    payload = {
        "model": XAI_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
    }

    try:

        response = _post(
            f"{XAI_BASE_URL}/chat/completions",
            _headers(XAI_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "XAI VISION ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "XAI VISION EXCEPTION:",
            exc
        )

        return None


# ============================================================
# MISTRAL VISION
# ============================================================

def _mistral_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not MISTRAL_API_KEY:
        return None

    print("VISION PROVIDER: MISTRAL")

    image_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )

    payload = {
        "model": MISTRAL_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "image_url",
                        "image_url": image_url,
                    },
                ],
            }
        ],
        "max_tokens": 4096,
    }

    try:

        response = _post(
            f"{MISTRAL_BASE_URL}/chat/completions",
            _headers(MISTRAL_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "MISTRAL VISION ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "MISTRAL VISION EXCEPTION:",
            exc
        )

        return None


# ============================================================
# GROQ VISION
# ============================================================

def _groq_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not GROQ_API_KEY:
        return None

    print("VISION PROVIDER: GROQ")

    image_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )

    payload = {
        "model": GROQ_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
    }

    try:

        response = _post(
            f"{GROQ_BASE_URL}/chat/completions",
            _headers(GROQ_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "GROQ VISION ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None

        return _extract_text(
            response.json()
        ) or None

    except Exception as exc:

        print(
            "GROQ VISION EXCEPTION:",
            exc
        )

        return None


# ============================================================
# XAI IMAGE GENERATION
# ============================================================

def _xai_image(
    prompt: str,
) -> Optional[str]:

    if not XAI_API_KEY:
        return None

    print("=" * 70)
    print("XAI IMAGE GENERATION REQUEST")
    print("=" * 70)
    print("MODEL:", XAI_IMAGE_MODEL)
    print("PROMPT:", prompt)

    payload = {
        "model": XAI_IMAGE_MODEL,
        "prompt": prompt,
        "response_format": "url",
    }

    try:

        response = _post(
            f"{XAI_BASE_URL}/images/generations",
            _headers(XAI_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "XAI IMAGE ERROR:",
                response.status_code,
                response.text[:1000],
            )

            return None

        data = response.json()

        url = _extract_image_url(data)

        if url:
            print(
                "XAI IMAGE SUCCESS:",
                url
            )

            return url

    except Exception as exc:

        print(
            "XAI IMAGE EXCEPTION:",
            exc
        )

    return None


# ============================================================
# XAI IMAGE EDIT
# ============================================================

def _xai_image_edit(
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not XAI_API_KEY:
        return None

    print("=" * 70)
    print("XAI IMAGE EDIT REQUEST")
    print("=" * 70)

    image_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )

    payload = {
        "model": XAI_IMAGE_MODEL,
        "prompt": prompt,
        "image": {
            "url": image_url,
            "type": "image_url",
        },
        "response_format": "url",
    }

    try:

        response = _post(
            f"{XAI_BASE_URL}/images/edits",
            _headers(XAI_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "XAI IMAGE EDIT ERROR:",
                response.status_code,
                response.text[:1000],
            )

            return None

        return _extract_image_url(
            response.json()
        )

    except Exception as exc:

        print(
            "XAI IMAGE EDIT EXCEPTION:",
            exc
        )

        return None


# ============================================================
# OPENROUTER IMAGE GENERATION
# ============================================================

def _openrouter_image(
    prompt: str,
) -> Optional[str]:

    if not OPENROUTER_API_KEY:
        return None

    print("=" * 70)
    print("OPENROUTER IMAGE GENERATION REQUEST")
    print("=" * 70)
    print("MODEL:", OPENROUTER_IMAGE_MODEL)
    print("PROMPT:", prompt)

    payload = {
        "model": OPENROUTER_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
    }

    try:

        response = _post(
            f"{OPENROUTER_BASE_URL}/images",
            _headers(OPENROUTER_API_KEY),
            payload,
        )

        if response.status_code >= 400:

            print(
                "OPENROUTER IMAGE ERROR:",
                response.status_code,
                response.text[:1000],
            )

            return None

        data = response.json()

        url = _extract_image_url(data)

        if url:
            print(
                "OPENROUTER IMAGE SUCCESS"
            )

            return url

    except Exception as exc:

        print(
            "OPENROUTER IMAGE EXCEPTION:",
            exc
        )

    return None


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def _mistral_image(
    prompt: str,
) -> Optional[str]:

    if not MISTRAL_API_KEY:
        return None

    print("=" * 70)
    print("MISTRAL IMAGE GENERATION REQUEST")
    print("=" * 70)
    print("MODEL:", MISTRAL_IMAGE_MODEL)
    print("PROMPT:", prompt)

    payload = {
        "model": MISTRAL_IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "tools": [
            {
                "type": "image_generation"
            }
        ],
    }

    try:

        for attempt in range(
            MISTRAL_MAX_RETRIES + 1
        ):

            print(
                "MISTRAL IMAGE ATTEMPT:",
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}"
            )

            response = _post(
                f"{MISTRAL_BASE_URL}/chat/completions",
                _headers(MISTRAL_API_KEY),
                payload,
            )

            if response.status_code == 429:

                if attempt >= MISTRAL_MAX_RETRIES:
                    return None

                retry_after = response.headers.get(
                    "Retry-After"
                )

                try:
                    delay = (
                        float(retry_after)
                        if retry_after
                        else (
                            MISTRAL_RETRY_BASE_SECONDS
                            * (2 ** attempt)
                        )
                    )
                except Exception:
                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        * (2 ** attempt)
                    )

                delay = min(delay, 30)

                time.sleep(delay)

                continue

            if response.status_code >= 400:

                print(
                    "MISTRAL IMAGE ERROR:",
                    response.status_code,
                    response.text[:1000],
                )

                return None

            data = response.json()

            url = _extract_image_url(data)

            if url:
                print(
                    "MISTRAL IMAGE SUCCESS"
                )

                return url

            text = _extract_text(data)

            if text:

                # Mistral can return the generated
                # image URL inside textual content.
                for part in text.split():

                    if (
                        part.startswith("https://")
                        and (
                            "mistral" in part
                            or "files." in part
                        )
                    ):
                        return part.strip(
                            "[](),"
                        )

            return None

    except Exception as exc:

        print(
            "MISTRAL IMAGE EXCEPTION:",
            exc
        )

    return None


# ============================================================
# GROQ IMAGE FALLBACK
# ============================================================

def _groq_image(
    prompt: str,
) -> Optional[str]:

    """
    Groq does NOT currently expose a native
    image-generation endpoint.

    This function exists so the provider slot
    remains compatible with the IDO AI routing
    system.

    It intentionally returns None instead of
    pretending that Groq generated an image.
    """

    if not GROQ_API_KEY:
        return None

    print(
        "GROQ IMAGE:",
        "NO NATIVE IMAGE GENERATION API"
    )

    return None


# ============================================================
# IMAGE GENERATION ROUTER
# ============================================================

def generate_image(
    prompt: str,
) -> Optional[str]:

    print("=" * 70)
    print("IMAGE GENERATION START")
    print("=" * 70)
    print("PROMPT:", prompt)

    # --------------------------------------------------------
    # 1. XAI
    # --------------------------------------------------------

    result = _xai_image(prompt)

    if result:
        print("IMAGE PROVIDER: XAI")
        return result

    # --------------------------------------------------------
    # 2. OpenRouter
    # --------------------------------------------------------

    result = _openrouter_image(prompt)

    if result:
        print("IMAGE PROVIDER: OPENROUTER")
        return result

    # --------------------------------------------------------
    # 3. Groq compatibility slot
    # --------------------------------------------------------

    result = _groq_image(prompt)

    if result:
        print("IMAGE PROVIDER: GROQ")
        return result

    # --------------------------------------------------------
    # 4. Mistral
    # --------------------------------------------------------

    result = _mistral_image(prompt)

    if result:
        print("IMAGE PROVIDER: MISTRAL")
        return result

    print(
        "IMAGE GENERATION FAILED:"
        " XAI + OPENROUTER + GROQ + MISTRAL"
    )

    return None


# ============================================================
# IMAGE EDIT ROUTER
# ============================================================

def edit_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    print("=" * 70)
    print("IMAGE EDITING START")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. XAI
    # --------------------------------------------------------

    result = _xai_image_edit(
        prompt,
        image_bytes,
        mime_type,
    )

    if result:
        print("IMAGE EDIT PROVIDER: XAI")
        return result

    # --------------------------------------------------------
    # 2. OpenRouter
    #
    # The dedicated OpenRouter image endpoint is used as
    # fallback. Some image models support reference images.
    # --------------------------------------------------------

    result = _openrouter_image(
        prompt
    )

    if result:
        print(
            "IMAGE EDIT PROVIDER: OPENROUTER"
        )

        return result

    # --------------------------------------------------------
    # 3. Mistral fallback
    # --------------------------------------------------------

    result = _mistral_image(
        prompt
    )

    if result:

        print(
            "IMAGE EDIT PROVIDER: MISTRAL"
        )

        return result

    print(
        "IMAGE EDITING FAILED"
    )

    return None


# ============================================================
# IMAGE REQUEST DETECTOR
# ============================================================

def is_image_request(
    message: str,
) -> bool:

    if not message:
        return False

    text = message.lower().strip()

    image_words = [
        "صورة",
        "صوره",
        "صور",
        "أنشئ صورة",
        "انشئ صورة",
        "انشئ صوره",
        "أنشئ صوره",
        "اعمل صورة",
        "اعمل صوره",
        "اصنع صورة",
        "اصنع صوره",
        "ارسم",
        "تصميم",
        "توليد صورة",
        "توليد صوره",
        "generate image",
        "generate a picture",
        "create image",
        "create a picture",
        "make an image",
        "make a picture",
        "draw",
        "image generation",
        "picture",
        "photo",
    ]

    edit_words = [
        "عدل الصورة",
        "عدل الصوره",
        "تعديل الصورة",
        "تعديل الصوره",
        "حرر الصورة",
        "حرر الصوره",
        "edit image",
        "edit the image",
        "modify image",
        "modify the image",
    ]

    return any(
        word in text
        for word in (
            image_words
            + edit_words
        )
    )


def is_image_edit_request(
    message: str,
) -> bool:

    if not message:
        return False

    text = message.lower()

    edit_words = [
        "عدل الصورة",
        "عدل الصوره",
        "تعديل الصورة",
        "تعديل الصوره",
        "حرر الصورة",
        "حرر الصوره",
        "edit image",
        "edit the image",
        "modify image",
        "modify the image",
        "change the image",
    ]

    return any(
        word in text
        for word in edit_words
    )


# ============================================================
# IMAGE RESPONSE
# ============================================================

def get_image_response(
    message: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
    conversation_id: Optional[str] = None,
):

    print("=" * 70)
    print("IMAGE REQUEST")
    print("MESSAGE:", message)
    print(
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )
    print("MIME TYPE:", mime_type)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # --------------------------------------------------------
    # IMAGE EDIT
    # --------------------------------------------------------

    if (
        image_bytes
        and is_image_edit_request(message)
    ):

        result = edit_image(
            message,
            image_bytes,
            mime_type or "image/png",
        )

        if result:
            return {
                "type": "image",
                "image_url": result,
                "provider": "xAI/OpenRouter/Mistral",
                "conversation_id": conversation_id,
            }

        return {
            "type": "error",
            "message": (
                "تعذر تعديل الصورة حاليًا."
            ),
            "conversation_id": conversation_id,
        }

    # --------------------------------------------------------
    # IMAGE GENERATION
    # --------------------------------------------------------

    result = generate_image(
        message
    )

    if result:

        return {
            "type": "image",
            "image_url": result,
            "provider": "xAI/OpenRouter/Mistral",
            "conversation_id": conversation_id,
        }

    return {
        "type": "error",
        "message": (
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة مزودي الصور المتاحين."
        ),
        "conversation_id": conversation_id,
    }


# ============================================================
# IMAGE UNDERSTANDING
# ============================================================

def analyze_image(
    message: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    print("=" * 70)
    print("IMAGE UNDERSTANDING START")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. XAI
    # --------------------------------------------------------

    result = _xai_vision(
        message,
        image_bytes,
        mime_type,
    )

    if result:
        print(
            "VISION PROVIDER: XAI"
        )

        return result

    # --------------------------------------------------------
    # 2. Mistral
    # --------------------------------------------------------

    result = _mistral_vision(
        message,
        image_bytes,
        mime_type,
    )

    if result:
        print(
            "VISION PROVIDER: MISTRAL"
        )

        return result

    # --------------------------------------------------------
    # 3. Groq
    # --------------------------------------------------------

    result = _groq_vision(
        message,
        image_bytes,
        mime_type,
    )

    if result:
        print(
            "VISION PROVIDER: GROQ"
        )

        return result

    return None


# ============================================================
# MAIN TEXT RESPONSE
# ============================================================

def get_response(
    message: str,
    conversation_id: Optional[str] = None,
):

    print("=" * 70)
    print("DYNAMIC AI RESPONSE")
    print("MESSAGE:", message)
    print("CONVERSATION ID:", conversation_id)
    print("=" * 70)

    # --------------------------------------------------------
    # Text provider routing
    # --------------------------------------------------------

    providers = [
        (
            "XAI",
            _xai_text,
        ),
        (
            "MISTRAL",
            _mistral_text,
        ),
        (
            "GROQ",
            _groq_text,
        ),
        (
            "OPENROUTER",
            _openrouter_text,
        ),
        (
            "GEMINI",
            _gemini_text,
        ),
    ]

    for provider_name, provider in providers:

        try:

            result = provider(message)

            if result:

                print("=" * 70)
                print("API CHAT SUCCESS")
                print("PROVIDER:", provider_name)
                print("=" * 70)

                return result

        except Exception as exc:

            print(
                f"{provider_name} PROVIDER ERROR:",
                exc
            )

    return (
        "عذرًا، لم أتمكن من الحصول على إجابة "
        "من مزودي الذكاء الاصطناعي المتاحين حاليًا."
    )


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message: str,
) -> str:

    result = get_response(
        message,
        conversation_id=None,
    )

    if isinstance(result, str):
        return result

    if isinstance(result, dict):

        text = result.get(
            "text"
        )

        if text:
            return str(text)

        message_text = result.get(
            "message"
        )

        if message_text:
            return str(message_text)

    return (
        "لم أتمكن من الحصول على إجابة حاليًا."
    )


# ============================================================
# COMPATIBILITY ROUTER
# ============================================================

def ask_ollama(
    message: str,
) -> Optional[str]:

    """
    Compatibility function.

    Ollama is intentionally not part of the final
    cloud provider routing unless explicitly configured.
    """

    ollama_url = os.getenv(
        "OLLAMA_URL",
        ""
    ).strip()

    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.1:8b"
    )

    if not ollama_url:
        return None

    try:

        response = requests.post(
            f"{ollama_url.rstrip('/')}/api/generate",
            json={
                "model": ollama_model,
                "prompt": message,
                "stream": False,
            },
            timeout=AI_REQUEST_TIMEOUT,
        )

        if response.status_code >= 400:
            return None

        data = response.json()

        return data.get(
            "response"
        )

    except Exception:

        return None


# ============================================================
# HEALTH / STATUS
# ============================================================

def provider_status():

    return {
        "xai": bool(XAI_API_KEY),
        "mistral": bool(MISTRAL_API_KEY),
        "groq": bool(GROQ_API_KEY),
        "openrouter": bool(
            OPENROUTER_API_KEY
        ),
        "gemini": bool(GEMINI_API_KEY),

        "text": [
            "xai",
            "mistral",
            "groq",
            "openrouter",
            "gemini",
        ],

        "vision": [
            "xai",
            "mistral",
            "groq",
        ],

        "image": [
            "xai",
            "openrouter",
            "mistral",
        ],
    }


# ============================================================
# STARTUP COMPATIBILITY
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
print("API BLUEPRINT: REGISTERED")
print("=" * 70)