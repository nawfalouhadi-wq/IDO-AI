import os
import base64
import uuid
import re
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

from google import genai
from google.genai.types import HttpOptions

from memory import (
    add_conversation_message,
    build_conversation_context,
    learn,
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# TIMEOUTS
# ============================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "5")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "30")),
)

IMAGE_TIMEOUT = (
    int(os.getenv("IMAGE_CONNECT_TIMEOUT", "5")),
    int(os.getenv("IMAGE_READ_TIMEOUT", "90")),
)


CONVERSATION_CONTEXT_LIMIT = int(
    os.getenv(
        "CONVERSATION_CONTEXT_LIMIT",
        "12",
    )
)


# ============================================================
# GENERATED IMAGE DIRECTORY
# ============================================================

GENERATED_IMAGE_DIR = Path(
    os.getenv(
        "GENERATED_IMAGE_DIR",
        "static/generated",
    )
)

try:
    GENERATED_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
except Exception as e:
    print("GENERATED IMAGE DIRECTORY ERROR:", e)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_RESOLUTION = os.getenv(
    "IMAGE_RESOLUTION",
    "2K",
).upper()


# ============================================================
# MODEL SETTINGS
# ============================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image",
)


XAI_MODEL = os.getenv(
    "XAI_MODEL",
    "grok-4.5",
)

XAI_VISION_MODEL = os.getenv(
    "XAI_VISION_MODEL",
    "grok-4.5",
)

XAI_IMAGE_MODEL = os.getenv(
    "XAI_IMAGE_MODEL",
    "grok-imagine-image-quality",
)


OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5",
)

OPENAI_VISION_MODEL = os.getenv(
    "OPENAI_VISION_MODEL",
    "gpt-5",
)

OPENAI_IMAGE_MODEL = os.getenv(
    "OPENAI_IMAGE_MODEL",
    "gpt-image-1",
)


MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "pixtral-12b-2409",
)

MISTRAL_IMAGE_AGENT_ID = os.getenv(
    "MISTRAL_IMAGE_AGENT_ID",
    "",
)


# ============================================================
# API KEYS
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
)

XAI_API_KEY = os.getenv(
    "XAI_API_KEY",
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
)

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
)

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
)


# ============================================================
# API URLS
# ============================================================

XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)

XAI_IMAGE_URL = (
    "https://api.x.ai/v1/images/generations"
)


OPENAI_URL = (
    "https://api.openai.com/v1/chat/completions"
)

OPENAI_IMAGE_URL = (
    "https://api.openai.com/v1/images/generations"
)


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)


MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini_client = None

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=30000,
            ),
        )

        print("GEMINI CLIENT: READY")
        print("GEMINI MODEL:", GEMINI_MODEL)
        print(
            "GEMINI IMAGE MODEL:",
            GEMINI_IMAGE_MODEL,
        )

    except Exception as e:

        print(
            "GEMINI CLIENT ERROR:",
            e,
        )

        gemini_client = None

else:

    print(
        "GEMINI_API_KEY: NOT FOUND"
    )


# ============================================================
# STARTUP STATUS
# ============================================================

print(
    "================================================="
)

print(
    "BRAIN.PY LOADED"
)

print(
    "TEXT ROUTE:"
)

print(
    "GEMINI -> GROK -> OPENAI -> MISTRAL"
)

print(
    "IMAGE ROUTE:"
)

print(
    "GEMINI -> GROK -> OPENAI -> MISTRAL"
)

print(
    "OPENROUTER:"
)

print(
    "OPTIONAL IMAGE/TEXT FALLBACK"
)

print(
    "IMAGE RESOLUTION:",
    IMAGE_RESOLUTION,
)

print(
    "================================================="
)


# ============================================================
# GENERIC HELPERS
# ============================================================

def clean_answer(answer):

    if answer is None:
        return None

    try:

        answer = str(
            answer
        ).strip()

        if not answer:
            return None

        return answer

    except Exception:

        return None


def normalize_text(text):

    if not text:
        return ""

    text = str(
        text
    ).strip().lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    text = (
        text
        .replace("ـ", "")
        .replace("ً", "")
        .replace("ٌ", "")
        .replace("ٍ", "")
        .replace("َ", "")
        .replace("ُ", "")
        .replace("ِ", "")
        .replace("ّ", "")
        .replace("ْ", "")
    )

    text = re.sub(
        r"[،,؛;:!?؟()\[\]{}\"'`]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def is_fast_failure(status_code):

    return status_code in {
        400,
        401,
        402,
        403,
        404,
        409,
        413,
        415,
        422,
        429,
        500,
        502,
        503,
        504,
    }


# ============================================================
# MEMORY
# ============================================================

def build_context_message(
    message,
    conversation_id=None,
    context_limit=CONVERSATION_CONTEXT_LIMIT,
):

    message = str(
        message or ""
    ).strip()

    if not message:
        return ""

    if not conversation_id:
        return message

    try:

        context = build_conversation_context(
            conversation_id,
            context_limit,
        )

    except Exception as e:

        print(
            "CONVERSATION CONTEXT ERROR:",
            e,
        )

        context = ""

    if not context:
        return message

    return (
        "أنت Ido AI، مساعد ذكاء اصطناعي متعدد "
        "اللغات.\n\n"
        "استخدم سياق المحادثة السابقة لفهم "
        "الرسالة الجديدة.\n\n"
        "## سياق المحادثة:\n\n"
        f"{context}\n\n"
        "## الرسالة الجديدة:\n\n"
        f"{message}\n\n"
        "أجب مباشرة عن الرسالة الجديدة."
    )


def save_ai_response(
    question,
    answer,
    conversation_id=None,
    source="ai",
):

    if not question or not answer:
        return

    try:

        learn(
            question,
            answer,
            source=source,
        )

    except Exception as e:

        print(
            "MEMORY LEARN ERROR:",
            e,
        )

    if conversation_id:

        try:

            add_conversation_message(
                question,
                answer,
                conversation_id=conversation_id,
            )

        except Exception as e:

            print(
                "CONVERSATION SAVE ERROR:",
                e,
            )


# ============================================================
# CHAT COMPLETION PARSER
# ============================================================

def extract_response_content(data):

    if not isinstance(
        data,
        dict,
    ):
        return None

    choices = data.get(
        "choices",
        [],
    )

    if not choices:
        return None

    message_data = choices[0].get(
        "message",
        {},
    )

    if not isinstance(
        message_data,
        dict,
    ):
        return None

    content = message_data.get(
        "content"
    )

    if isinstance(
        content,
        str,
    ):
        return clean_answer(
            content
        )

    if isinstance(
        content,
        list,
    ):

        parts = []

        for item in content:

            if isinstance(
                item,
                dict,
            ):

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


# ============================================================
# IMAGE SAVING
# ============================================================

def save_generated_image(
    image_bytes,
):

    if not image_bytes:
        return None

    try:

        filename = (
            "aido_generated_"
            f"{uuid.uuid4().hex}.png"
        )

        file_path = (
            GENERATED_IMAGE_DIR /
            filename
        )

        file_path.write_bytes(
            image_bytes
        )

        return (
            "/static/generated/"
            + filename
        )

    except Exception as e:

        print(
            "SAVE GENERATED IMAGE ERROR:",
            e,
        )

        return None


def download_image_url(
    image_url,
):

    if not image_url:
        return None

    try:

        response = requests.get(
            image_url,
            timeout=IMAGE_TIMEOUT,
        )

        if response.status_code != 200:
            return None

        content_type = (
            response.headers
            .get(
                "Content-Type",
                "",
            )
            .lower()
        )

        if (
            "image" not in content_type
            and not response.content
        ):
            return None

        return save_generated_image(
            response.content
        )

    except Exception as e:

        print(
            "DOWNLOAD IMAGE ERROR:",
            e,
        )

        return None


# ============================================================
# DEEP BASE64 EXTRACTION
# ============================================================

def extract_base64_images(
    data,
):

    found = []

    if data is None:
        return found

    if isinstance(
        data,
        dict,
    ):

        for key, value in data.items():

            key_text = str(
                key
            ).lower()

            if key_text in {
                "b64_json",
                "base64",
                "image_base64",
            }:

                if (
                    isinstance(
                        value,
                        str,
                    )
                    and value.strip()
                ):

                    found.append(
                        value.strip()
                    )

            else:

                found.extend(
                    extract_base64_images(
                        value
                    )
                )

        return found

    if isinstance(
        data,
        list,
    ):

        for item in data:

            found.extend(
                extract_base64_images(
                    item
                )
            )

        return found

    return found


def extract_image_urls(
    data,
):

    found = []

    if data is None:
        return found

    if isinstance(
        data,
        str,
    ):

        urls = re.findall(
            r"https?://[^\s\"'<>]+",
            data,
        )

        for url in urls:

            url = url.rstrip(
                ".,);]"
            )

            if any(
                item in url.lower()
                for item in (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    "image",
                    "images",
                    "imgen",
                )
            ):

                found.append(
                    url
                )

        return found

    if isinstance(
        data,
        dict,
    ):

        for value in data.values():

            found.extend(
                extract_image_urls(
                    value
                )
            )

        return found

    if isinstance(
        data,
        list,
    ):

        for item in data:

            found.extend(
                extract_image_urls(
                    item
                )
            )

    return found


# ============================================================
# 1. GEMINI TEXT
# ============================================================

def ask_gemini(
    message,
):

    if gemini_client is None:
        return None

    if not message:
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
                contents=message,
            )
        )

        answer = clean_answer(
            getattr(
                response,
                "text",
                None,
            )
        )

        if answer:

            print(
                "Gemini response received."
            )

            return answer

    except Exception as e:

        print(
            "Gemini ERROR:",
            e,
        )

    return None


# ============================================================
# 2. GEMINI IMAGE
# ============================================================

def generate_image_with_gemini(
    prompt,
):

    if gemini_client is None:
        return None

    if not prompt:
        return None

    try:

        print(
            "Trying Gemini Image..."
        )

        response = (
            gemini_client
            .models
            .generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=prompt,
                config={
                    "response_modalities": [
                        "TEXT",
                        "IMAGE",
                    ],
                    "image_config": {
                        "image_size":
                            IMAGE_RESOLUTION,
                    },
                },
            )
        )

        candidates = getattr(
            response,
            "candidates",
            None,
        )

        if not candidates:
            return None

        for candidate in candidates:

            content = getattr(
                candidate,
                "content",
                None,
            )

            if not content:
                continue

            parts = getattr(
                content,
                "parts",
                None,
            )

            if not parts:
                continue

            for part in parts:

                inline_data = getattr(
                    part,
                    "inline_data",
                    None,
                )

                if not inline_data:
                    continue

                image_data = getattr(
                    inline_data,
                    "data",
                    None,
                )

                if not image_data:
                    continue

                image_url = (
                    save_generated_image(
                        image_data
                    )
                )

                if image_url:

                    print(
                        "Gemini Image: SUCCESS"
                    )

                    return image_url

    except Exception as e:

        print(
            "Gemini IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# 3. GROK / xAI TEXT
# ============================================================

def ask_grok(
    message,
):

    if not XAI_API_KEY:
        return None

    if not message:
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
                    "application/json",
            },
            json={
                "model":
                    XAI_MODEL,
                "messages": [
                    {
                        "role":
                            "user",
                        "content":
                            message,
                    }
                ],
            },
            timeout=REQUEST_TIMEOUT,
        )

        print(
            "xAI Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "xAI Response:",
                response.text[:1000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "xAI ERROR:",
            e,
        )

        return None


# ============================================================
# 4. GROK / xAI IMAGE
# ============================================================

def generate_image_with_grok(
    prompt,
):

    if not XAI_API_KEY:
        return None

    if not prompt:
        return None

    try:

        print(
            "Trying xAI / Grok Image..."
        )

        response = requests.post(
            XAI_IMAGE_URL,
            headers={
                "Authorization":
                    f"Bearer {XAI_API_KEY}",
                "Content-Type":
                    "application/json",
            },
            json={
                "model":
                    XAI_IMAGE_MODEL,
                "prompt":
                    prompt,
            },
            timeout=IMAGE_TIMEOUT,
        )

        print(
            "xAI IMAGE Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "xAI IMAGE Response:",
                response.text[:1500],
            )

            return None

        data = response.json()

        base64_images = (
            extract_base64_images(
                data
            )
        )

        for encoded in base64_images:

            try:

                if "," in encoded:

                    encoded = (
                        encoded
                        .split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = (
                    base64.b64decode(
                        encoded
                    )
                )

                image_url = (
                    save_generated_image(
                        image_bytes
                    )
                )

                if image_url:
                    return image_url

            except Exception:
                continue

        urls = extract_image_urls(
            data
        )

        if urls:

            return download_image_url(
                urls[0]
            )

    except Exception as e:

        print(
            "xAI IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# 5. OPENAI TEXT
# ============================================================

def ask_openai(
    message,
):

    if not OPENAI_API_KEY:
        return None

    if not message:
        return None

    try:

        print(
            "Trying OpenAI..."
        )

        response = requests.post(
            OPENAI_URL,
            headers={
                "Authorization":
                    f"Bearer {OPENAI_API_KEY}",
                "Content-Type":
                    "application/json",
            },
            json={
                "model":
                    OPENAI_MODEL,
                "messages": [
                    {
                        "role":
                            "user",
                        "content":
                            message,
                    }
                ],
            },
            timeout=REQUEST_TIMEOUT,
        )

        print(
            "OpenAI Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenAI Response:",
                response.text[:1000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "OpenAI ERROR:",
            e,
        )

        return None


# ============================================================
# 6. OPENAI IMAGE
# ============================================================

def generate_image_with_openai(
    prompt,
):

    if not OPENAI_API_KEY:
        return None

    if not prompt:
        return None

    try:

        print(
            "Trying OpenAI Image..."
        )

        response = requests.post(
            OPENAI_IMAGE_URL,
            headers={
                "Authorization":
                    f"Bearer {OPENAI_API_KEY}",
                "Content-Type":
                    "application/json",
            },
            json={
                "model":
                    OPENAI_IMAGE_MODEL,
                "prompt":
                    prompt,
            },
            timeout=IMAGE_TIMEOUT,
        )

        print(
            "OpenAI IMAGE Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenAI IMAGE Response:",
                response.text[:1500],
            )

            return None

        data = response.json()

        base64_images = (
            extract_base64_images(
                data
            )
        )

        for encoded in base64_images:

            try:

                if "," in encoded:

                    encoded = (
                        encoded
                        .split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = (
                    base64.b64decode(
                        encoded
                    )
                )

                image_url = (
                    save_generated_image(
                        image_bytes
                    )
                )

                if image_url:
                    return image_url

            except Exception:
                continue

        urls = extract_image_urls(
            data
        )

        if urls:

            return download_image_url(
                urls[0]
            )

    except Exception as e:

        print(
            "OpenAI IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# 7. MISTRAL TEXT
# ============================================================

def ask_mistral(
    message,
):

    if not MISTRAL_API_KEY:
        return None

    if not message:
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
                    "application/json",
            },
            json={
                "model":
                    MISTRAL_MODEL,
                "messages": [
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
                    1024,
            },
            timeout=REQUEST_TIMEOUT,
        )

        print(
            "Mistral Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Mistral Response:",
                response.text[:1000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "Mistral ERROR:",
            e,
        )

    return None


# ============================================================
# 8. MISTRAL IMAGE
# ============================================================

def generate_image_with_mistral(
    prompt,
):

    if not MISTRAL_API_KEY:
        return None

    if not prompt:
        return None

    if not MISTRAL_IMAGE_AGENT_ID:

        print(
            "MISTRAL IMAGE AGENT ID: "
            "NOT CONFIGURED"
        )

        return None

    try:

        print(
            "Trying Mistral Image Agent..."
        )

        response = requests.post(
            "https://api.mistral.ai/v1/agents/completions",
            headers={
                "Authorization":
                    f"Bearer {MISTRAL_API_KEY}",
                "Content-Type":
                    "application/json",
            },
            json={
                "agent_id":
                    MISTRAL_IMAGE_AGENT_ID,
                "messages": [
                    {
                        "role":
                            "user",
                        "content":
                            prompt,
                    }
                ],
            },
            timeout=IMAGE_TIMEOUT,
        )

        print(
            "Mistral IMAGE Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Mistral IMAGE Response:",
                response.text[:1500],
            )

            return None

        data = response.json()

        base64_images = (
            extract_base64_images(
                data
            )
        )

        for encoded in base64_images:

            try:

                if "," in encoded:

                    encoded = (
                        encoded
                        .split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = (
                    base64.b64decode(
                        encoded
                    )
                )

                image_url = (
                    save_generated_image(
                        image_bytes
                    )
                )

                if image_url:
                    return image_url

            except Exception:
                continue

        urls = extract_image_urls(
            data
        )

        if urls:

            return download_image_url(
                urls[0]
            )

    except Exception as e:

        print(
            "MISTRAL IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# OPENROUTER OPTIONAL TEXT FALLBACK
# ============================================================

def ask_openrouter(
    message,
):

    if not OPENROUTER_API_KEY:
        return None

    try:

        print(
            "Trying OpenRouter..."
        )

        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":
                    "application/json",
                "X-Title":
                    "Ido AI",
            },
            json={
                "model":
                    "openrouter/free",
                "messages": [
                    {
                        "role":
                            "user",
                        "content":
                            message,
                    }
                ],
            },
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:

            print(
                "OpenRouter Status:",
                response.status_code,
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "OpenRouter ERROR:",
            e,
        )

        return None


# ============================================================
# OPENROUTER IMAGE
# ============================================================

def generate_image_with_openrouter(
    prompt,
):

    if not OPENROUTER_API_KEY:
        return None

    model = os.getenv(
        "OPENROUTER_IMAGE_MODEL",
        "",
    ).strip()

    if not model:

        print(
            "OPENROUTER IMAGE MODEL: "
            "NOT CONFIGURED"
        )

        return None

    try:

        print(
            "Trying OpenRouter Image..."
        )

        response = requests.post(
            OPENROUTER_IMAGE_URL,
            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":
                    "application/json",
                "X-Title":
                    "Ido AI",
            },
            json={
                "model":
                    model,
                "prompt":
                    prompt,
            },
            timeout=IMAGE_TIMEOUT,
        )

        print(
            "OpenRouter IMAGE Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenRouter IMAGE Response:",
                response.text[:1500],
            )

            return None

        data = response.json()

        base64_images = (
            extract_base64_images(
                data
            )
        )

        for encoded in base64_images:

            try:

                if "," in encoded:

                    encoded = (
                        encoded
                        .split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = (
                    base64.b64decode(
                        encoded
                    )
                )

                image_url = (
                    save_generated_image(
                        image_bytes
                    )
                )

                if image_url:
                    return image_url

            except Exception:
                continue

        urls = extract_image_urls(
            data
        )

        if urls:

            return download_image_url(
                urls[0]
            )

    except Exception as e:

        print(
            "OpenRouter IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# IMAGE ROUTER
#
# Gemini
#   ↓
# Grok
#   ↓
# OpenAI
#   ↓
# Mistral
#   ↓
# OpenRouter (optional)
# ============================================================

def generate_image(
    prompt,
):

    prompt = str(
        prompt or ""
    ).strip()

    if not prompt:
        return None

    print(
        "===================================="
    )

    print(
        "IMAGE GENERATION STARTED"
    )

    print(
        "IMAGE PROMPT:",
        prompt,
    )

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    result = (
        generate_image_with_gemini(
            prompt
        )
    )

    if result:
        return result

    print(
        "Gemini Image failed -> NEXT"
    )

    # --------------------------------------------------------
    # Grok
    # --------------------------------------------------------

    result = (
        generate_image_with_grok(
            prompt
        )
    )

    if result:
        return result

    print(
        "Grok Image failed -> NEXT"
    )

    # --------------------------------------------------------
    # OpenAI
    # --------------------------------------------------------

    result = (
        generate_image_with_openai(
            prompt
        )
    )

    if result:
        return result

    print(
        "OpenAI Image failed -> NEXT"
    )

    # --------------------------------------------------------
    # Mistral
    # --------------------------------------------------------

    result = (
        generate_image_with_mistral(
            prompt
        )
    )

    if result:
        return result

    print(
        "Mistral Image failed -> NEXT"
    )

    # --------------------------------------------------------
    # OpenRouter optional fallback
    # --------------------------------------------------------

    result = (
        generate_image_with_openrouter(
            prompt
        )
    )

    if result:
        return result

    print(
        "IMAGE GENERATION FAILED"
    )

    return None


# ============================================================
# BUILTIN RESPONSES
# ============================================================

BUILTIN_RESPONSES = {

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

    "السلام عليكم":
        "وعليكم السلام ورحمة الله وبركاته. "
        "كيف يمكنني مساعدتك؟",

    "اسمك":
        "أنا Ido AI.",

    "ما اسمك":
        "أنا Ido AI.",

    "من صنعك":
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI.",

    "من طورك":
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI.",

    "شكرا":
        "على الرحب والسعة.",

    "وداعا":
        "إلى اللقاء! أتمنى لك يومًا سعيدًا.",
}


# ============================================================
# IMAGE INTENT
# ============================================================

def is_image_generation_request(
    message,
):

    text = normalize_text(
        message
    )

    if not text:
        return False

    image_words = (
        "صورة",
        "صوره",
        "image",
        "picture",
        "artwork",
    )

    generation_words = (
        "ولد",
        "انشئ",
        "انشاء",
        "اصنع",
        "ارسم",
        "صمم",
        "اعمل",
        "توليد",
        "تنشئ",
        "تولد",
        "generate",
        "create",
        "make",
        "draw",
    )

    has_image = any(
        word in text
        for word in image_words
    )

    has_generation = any(
        word in text
        for word in generation_words
    )

    if has_image and has_generation:

        print(
            "IMAGE GENERATION INTENT DETECTED:",
            text,
        )

        return True

    return False


def get_image_prompt(
    message,
):

    text = str(
        message or ""
    ).strip()

    if not text:
        return (
            "Create a beautiful "
            "high-quality image."
        )

    # Remove common commands.

    patterns = [
        r"^.*?انشئ\s+لي\s+صوره\s*",
        r"^.*?انشئ\s+لي\s+صورة\s*",
        r"^.*?انشئ\s+صورة\s*",
        r"^.*?انشئ\s+صوره\s*",
        r"^.*?اصنع\s+لي\s+صورة\s*",
        r"^.*?اصنع\s+صورة\s*",
        r"^.*?ارسم\s+لي\s+صورة\s*",
        r"^.*?ارسم\s+صورة\s*",
        r"^.*?generate\s+an?\s+image\s*",
        r"^.*?create\s+an?\s+image\s*",
        r"^.*?make\s+an?\s+image\s*",
    ]

    for pattern in patterns:

        cleaned = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

        if cleaned != text:

            text = cleaned.strip()
            break

    text = text.strip(
        " \t\n\r.,،:؛!?؟"
    )

    if not text:

        return (
            "Create a beautiful "
            "high-quality photorealistic image "
            "with cinematic lighting, realistic "
            "details and professional composition."
        )

    return text


# ============================================================
# MAIN TEXT RESPONSE
# ============================================================

def get_response(
    message,
    conversation_id=None,
    save_response=True,
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

    # ========================================================
    # IMAGE
    # ========================================================

    if is_image_generation_request(
        original_message
    ):

        image_prompt = get_image_prompt(
            original_message
        )

        generated = generate_image(
            image_prompt
        )

        if generated:

            if (
                save_response
                and conversation_id
            ):

                save_ai_response(
                    original_message,
                    "تم إنشاء الصورة بنجاح.",
                    conversation_id,
                    source="image_generation",
                )

            return (
                "IMAGE_URL:"
                + generated
            )

        return (
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة Gemini وGrok وOpenAI "
            "وMistral، ولم يُرجع أي مولد صورة "
            "نتيجة صالحة."
        )

    # ========================================================
    # BUILTIN
    # ========================================================

    normalized = normalize_text(
        original_message
    )

    builtin = (
        BUILTIN_RESPONSES.get(
            normalized
        )
    )

    if builtin:

        if (
            save_response
            and conversation_id
        ):

            save_ai_response(
                original_message,
                builtin,
                conversation_id,
                source="builtin",
            )

        return builtin

    # ========================================================
    # CONTEXT
    # ========================================================

    model_message = build_context_message(
        original_message,
        conversation_id,
    )

    # ========================================================
    # GEMINI
    # ========================================================

    answer = ask_gemini(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="gemini",
            )

        return answer

    print(
        "Gemini failed -> Grok"
    )

    # ========================================================
    # GROK
    # ========================================================

    answer = ask_grok(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="grok",
            )

        return answer

    print(
        "Grok failed -> OpenAI"
    )

    # ========================================================
    # OPENAI
    # ========================================================

    answer = ask_openai(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="openai",
            )

        return answer

    print(
        "OpenAI failed -> Mistral"
    )

    # ========================================================
    # MISTRAL
    # ========================================================

    answer = ask_mistral(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="mistral",
            )

        return answer

    # ========================================================
    # OPTIONAL OPENROUTER
    # ========================================================

    print(
        "Mistral failed -> OpenRouter"
    )

    answer = ask_openrouter(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="openrouter",
            )

        return answer

    # ========================================================
    # TOTAL FAILURE
    # ========================================================

    fallback = (
        "أنا Ido AI، ولكن جميع مزودي الذكاء "
        "الاصطناعي المتاحين حاليًا لم يعيدوا "
        "إجابة صالحة."
    )

    if save_response:

        save_ai_response(
            original_message,
            fallback,
            conversation_id,
            source="fallback",
        )

    return fallback


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def get_image_response(
    message,
    image_bytes,
    mime_type,
    conversation_id=None,
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

    # --------------------------------------------------------
    # Convert image to data URL
    # --------------------------------------------------------

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )

    image_data_url = (
        f"data:{mime_type};base64,"
        f"{encoded}"
    )

    # --------------------------------------------------------
    # OpenAI Vision
    # --------------------------------------------------------

    if OPENAI_API_KEY:

        try:

            response = requests.post(
                OPENAI_URL,
                headers={
                    "Authorization":
                        f"Bearer {OPENAI_API_KEY}",
                    "Content-Type":
                        "application/json",
                },
                json={
                    "model":
                        OPENAI_VISION_MODEL,
                    "messages": [
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
                                            image_data_url
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:

                answer = (
                    extract_response_content(
                        response.json()
                    )
                )

                if answer:
                    return answer

        except Exception as e:

            print(
                "OpenAI VISION ERROR:",
                e,
            )

    # --------------------------------------------------------
    # Grok Vision
    # --------------------------------------------------------

    if XAI_API_KEY:

        try:

            response = requests.post(
                XAI_URL,
                headers={
                    "Authorization":
                        f"Bearer {XAI_API_KEY}",
                    "Content-Type":
                        "application/json",
                },
                json={
                    "model":
                        XAI_VISION_MODEL,
                    "messages": [
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
                                            image_data_url
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:

                answer = (
                    extract_response_content(
                        response.json()
                    )
                )

                if answer:
                    return answer

        except Exception as e:

            print(
                "GROK VISION ERROR:",
                e,
            )

    # --------------------------------------------------------
    # Mistral Vision
    # --------------------------------------------------------

    if MISTRAL_API_KEY:

        try:

            response = requests.post(
                MISTRAL_URL,
                headers={
                    "Authorization":
                        f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type":
                        "application/json",
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
                                        message,
                                },
                                {
                                    "type":
                                        "image_url",
                                    "image_url": {
                                        "url":
                                            image_data_url
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:

                answer = (
                    extract_response_content(
                        response.json()
                    )
                )

                if answer:
                    return answer

        except Exception as e:

            print(
                "MISTRAL VISION ERROR:",
                e,
            )

    return (
        "تعذر تحليل الصورة حاليًا."
    )