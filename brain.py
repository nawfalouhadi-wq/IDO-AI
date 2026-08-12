# =========================================================
# Ido AI - BRAIN.PY
# =========================================================
# Text:
#   Gemini -> Grok -> Groq -> OpenRouter -> Mistral
#
# Image generation:
#   Pollinations -> XAI -> OpenRouter
#
# Image understanding:
#   Gemini -> XAI -> Groq -> Mistral -> OpenRouter
#
# IMPORTANT:
#   API keys must stay inside .env / Railway Variables.
# =========================================================

import os
import base64
import requests

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GENERAL SETTINGS
# =========================================================

CONNECT_TIMEOUT = int(
    os.getenv("REQUEST_CONNECT_TIMEOUT", "3")
)

READ_TIMEOUT = int(
    os.getenv("REQUEST_READ_TIMEOUT", "12")
)

REQUEST_TIMEOUT = (
    CONNECT_TIMEOUT,
    READ_TIMEOUT
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKENS", "1024")
)


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

gemini_client = None


if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=3000
            )
        )

        print("GEMINI CLIENT: READY")
        print(
            "GEMINI MODEL:",
            GEMINI_MODEL
        )

    except Exception as e:

        print(
            "GEMINI CLIENT ERROR:",
            e
        )

        gemini_client = None

else:

    print(
        "GEMINI_API_KEY: NOT FOUND"
    )


# =========================================================
# XAI / GROK
# =========================================================

XAI_API_KEY = os.getenv(
    "XAI_API_KEY"
)

XAI_URL = (
    "https://api.x.ai/v1/chat/completions"
)

XAI_IMAGE_URL = (
    "https://api.x.ai/v1/images/generations"
)

XAI_MODEL = os.getenv(
    "XAI_MODEL",
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


if XAI_API_KEY:

    print("XAI / GROK CLIENT: READY")
    print(
        "XAI MODEL:",
        XAI_MODEL
    )
    print(
        "XAI VISION MODEL:",
        XAI_VISION_MODEL
    )
    print(
        "XAI IMAGE MODEL:",
        XAI_IMAGE_MODEL
    )

else:

    print(
        "XAI_API_KEY: NOT FOUND"
    )


# =========================================================
# GROQ
# =========================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)


if GROQ_API_KEY:

    print("GROQ CLIENT: READY")
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


# =========================================================
# OPENROUTER
# =========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "google/gemini-2.5-flash-image"
)


if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
    )

    print(
        "OPENROUTER MODEL:",
        OPENROUTER_MODEL
    )

    print(
        "OPENROUTER IMAGE MODEL:",
        OPENROUTER_IMAGE_MODEL
    )

else:

    print(
        "OPENROUTER_API_KEY: NOT FOUND"
    )


# =========================================================
# POLLINATIONS
# =========================================================

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/image/"
)

POLLINATIONS_IMAGE_MODEL = os.getenv(
    "POLLINATIONS_IMAGE_MODEL",
    "flux"
)


if POLLINATIONS_API_KEY:

    print(
        "POLLINATIONS CLIENT: READY"
    )

    print(
        "POLLINATIONS IMAGE MODEL:",
        POLLINATIONS_IMAGE_MODEL
    )

else:

    print(
        "POLLINATIONS_API_KEY: NOT FOUND"
    )


# =========================================================
# MISTRAL
# =========================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
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


# =========================================================
# STARTUP INFORMATION
# =========================================================

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
    "GEMINI -> GROK -> GROQ -> "
    "OPENROUTER -> MISTRAL"
)

print(
    "IMAGE ROUTE:"
)

print(
    "POLLINATIONS -> XAI -> OPENROUTER"
)

print(
    "VISION ROUTE:"
)

print(
    "GEMINI -> XAI -> GROQ -> "
    "MISTRAL -> OPENROUTER"
)

print(
    "================================================="
)


# =========================================================
# CLEAN TEXT
# =========================================================

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


# =========================================================
# GENERIC OPENAI-COMPATIBLE RESPONSE PARSER
# =========================================================

def extract_chat_answer(data):

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

    message_data = choices[0].get(
        "message",
        {}
    )

    content = message_data.get(
        "content"
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

            if item.get("type") == "text":

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


# =========================================================
# GEMINI - TEXT
# =========================================================

def ask_gemini(message):

    if gemini_client is None:

        print(
            "Gemini SKIPPED: client unavailable."
        )

        return None

    if not message:
        return None

    try:

        print(
            "Trying Gemini..."
        )

        response = (
            gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=message
            )
        )

        if response:

            answer = clean_answer(
                response.text
            )

            if answer:

                print(
                    "Gemini response received."
                )

                return answer

        print(
            "Gemini returned empty response."
        )

        return None

    except Exception as e:

        print(
            "Gemini FAILED:",
            str(e)[:1000]
        )

        return None


# =========================================================
# XAI / GROK - TEXT
# =========================================================

def ask_xai(message):

    if not XAI_API_KEY:

        print(
            "Grok SKIPPED: XAI_API_KEY missing."
        )

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
                    0.7,

                "max_tokens":
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI / Grok Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI / Grok FAILED:",
                response.text[:1000]
            )

            return None

        data = response.json()

        answer = extract_chat_answer(
            data
        )

        if answer:

            print(
                "xAI / Grok response received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "xAI / Grok ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# GROQ - TEXT
# =========================================================

def ask_groq(message):

    if not GROQ_API_KEY:

        print(
            "Groq SKIPPED: API key missing."
        )

        return None

    if not message:
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
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "Groq ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# OPENROUTER - TEXT
# =========================================================

def ask_openrouter(message):

    if not OPENROUTER_API_KEY:

        print(
            "OpenRouter SKIPPED: API key missing."
        )

        return None

    if not message:
        return None

    try:

        print(
            "Trying OpenRouter..."
        )

        response = requests.post(
            OPENROUTER_CHAT_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "X-Title":
                    "Ido AI"
            },

            json={
                "model":
                    OPENROUTER_MODEL,

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
                "OpenRouter FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "OpenRouter response received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "OpenRouter ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# MISTRAL - TEXT
# =========================================================

def ask_mistral(message):

    if not MISTRAL_API_KEY:

        print(
            "Mistral SKIPPED: API key missing."
        )

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
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "Mistral response received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "Mistral ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# POLLINATIONS - IMAGE GENERATION
# =========================================================

def generate_pollinations_image(
    prompt
):

    if not POLLINATIONS_API_KEY:

        print(
            "Pollinations SKIPPED: "
            "POLLINATIONS_API_KEY missing."
        )

        return None

    if not prompt:

        return None

    try:

        print(
            "Pollinations IMAGE GENERATION STARTED"
        )

        print(
            "Pollinations IMAGE MODEL:",
            POLLINATIONS_IMAGE_MODEL
        )

        print(
            "Pollinations PROMPT:",
            prompt
        )

        response = requests.get(
            POLLINATIONS_IMAGE_URL
            + requests.utils.quote(
                prompt,
                safe=""
            ),

            headers={
                "Authorization":
                    f"Bearer {POLLINATIONS_API_KEY}"
            },

            params={
                "model":
                    POLLINATIONS_IMAGE_MODEL,

                "width":
                    2048,

                "height":
                    2048,

                "n":
                    1
            },

            timeout=(
                5,
                60
            )
        )

        print(
            "Pollinations IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Pollinations IMAGE ERROR:",
                response.text[:1000]
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

            print(
                "Pollinations returned "
                "non-image content."
            )

            return None

        image_base64 = base64.b64encode(
            response.content
        ).decode(
            "utf-8"
        )

        data_url = (
            f"data:{content_type};base64,"
            f"{image_base64}"
        )

        print(
            "Pollinations image received."
        )

        return data_url

    except requests.exceptions.Timeout:

        print(
            "Pollinations IMAGE ERROR: timeout."
        )

        return None

    except Exception as e:

        print(
            "Pollinations IMAGE ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# XAI / GROK - IMAGE GENERATION
# =========================================================

def generate_xai_image(
    prompt
):

    if not XAI_API_KEY:

        print(
            "xAI IMAGE SKIPPED: API key missing."
        )

        return None

    if not prompt:
        return None

    try:

        print(
            "XAI / GROK IMAGE GENERATION STARTED"
        )

        print(
            "XAI IMAGE MODEL:",
            XAI_IMAGE_MODEL
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

                "response_format":
                    "url",

                "n":
                    1,

                "resolution":
                    "2k"
            },

            timeout=(
                5,
                45
            )
        )

        print(
            "xAI IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI IMAGE FAILED:",
                response.text[:1000]
            )

            return None

        data = response.json()

        images = data.get(
            "data",
            []
        )

        if not images:

            print(
                "xAI IMAGE: empty data."
            )

            return None

        image_url = images[0].get(
            "url"
        )

        if image_url:

            print(
                "xAI IMAGE RECEIVED."
            )

            return image_url

        return None

    except Exception as e:

        print(
            "xAI IMAGE ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# OPENROUTER - IMAGE GENERATION
# =========================================================

def generate_openrouter_image(
    prompt
):

    if not OPENROUTER_API_KEY:

        print(
            "OpenRouter IMAGE SKIPPED: "
            "API key missing."
        )

        return None

    if not prompt:
        return None

    try:

        print(
            "OPENROUTER IMAGE GENERATION STARTED"
        )

        print(
            "OPENROUTER IMAGE MODEL:",
            OPENROUTER_IMAGE_MODEL
        )

        response = requests.post(
            OPENROUTER_IMAGE_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "X-Title":
                    "Ido AI"
            },

            json={
                "model":
                    OPENROUTER_IMAGE_MODEL,

                "prompt":
                    prompt,

                "n":
                    1
            },

            timeout=(
                5,
                60
            )
        )

        print(
            "OpenRouter IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter IMAGE FAILED:",
                response.text[:1000]
            )

            return None

        data = response.json()

        images = data.get(
            "data",
            []
        )

        if not images:

            print(
                "OpenRouter IMAGE: empty data."
            )

            return None

        image = images[0]

        b64_json = image.get(
            "b64_json"
        )

        if b64_json:

            media_type = image.get(
                "media_type",
                "image/png"
            )

            image_url = (
                f"data:{media_type};base64,"
                f"{b64_json}"
            )

            print(
                "OpenRouter image received."
            )

            return image_url

        image_url = image.get(
            "url"
        )

        if image_url:

            print(
                "OpenRouter image URL received."
            )

            return image_url

        return None

    except Exception as e:

        print(
            "OpenRouter IMAGE ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# IMAGE GENERATION ROUTER
# =========================================================

def generate_image(
    prompt
):

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
        prompt
    )

    print(
        "===================================="
    )


    # -----------------------------------------------------
    # 1. POLLINATIONS
    # -----------------------------------------------------

    image_url = (
        generate_pollinations_image(
            prompt
        )
    )

    if image_url:

        print(
            "IMAGE SUCCESS: POLLINATIONS"
        )

        return image_url

    print(
        "Pollinations failed."
    )


    # -----------------------------------------------------
    # 2. XAI
    # -----------------------------------------------------

    image_url = (
        generate_xai_image(
            prompt
        )
    )

    if image_url:

        print(
            "IMAGE SUCCESS: XAI"
        )

        return image_url

    print(
        "xAI image failed."
    )


    # -----------------------------------------------------
    # 3. OPENROUTER
    # -----------------------------------------------------

    image_url = (
        generate_openrouter_image(
            prompt
        )
    )

    if image_url:

        print(
            "IMAGE SUCCESS: OPENROUTER"
        )

        return image_url

    print(
        "OpenRouter image failed."
    )


    # -----------------------------------------------------
    # ALL FAILED
    # -----------------------------------------------------

    print(
        "IMAGE GENERATION FAILED."
    )

    return None


# =========================================================
# IMAGE GENERATION INTENT
# =========================================================

def is_image_generation_request(
    message
):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    image_words = [

        # Arabic
        "أنشئ صورة",
        "انشئ صورة",
        "أنشئ لي صورة",
        "انشئ لي صورة",
        "اصنع صورة",
        "اصنع لي صورة",
        "صنع صورة",
        "إنشاء صورة",
        "انشاء صورة",
        "ولد صورة",
        "ولّد صورة",
        "وليد صورة",
        "ارسم صورة",
        "ارسم لي",
        "صورة لي",

        # English
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
        "make a picture"
    ]

    for word in image_words:

        if word in text:

            return True

    return False


# =========================================================
# EXTRACT IMAGE PROMPT
# =========================================================

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

        "generate an image of",
        "generate image of",
        "create an image of",
        "create image of",
        "make an image of",
        "make image of",
        "generate a picture of",
        "create a picture of",
        "make a picture of"
    ]

    lower_text = text.lower()

    for prefix in prefixes:

        if lower_text.startswith(
            prefix.lower()
        ):

            prompt = text[
                len(prefix):
            ].strip()

            return prompt

    return text


# =========================================================
# XAI - IMAGE UNDERSTANDING
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

    try:

        print(
            "Trying xAI / Grok with image..."
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
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
                                    message
                            },
                            {
                                "type":
                                    "image_url",

                                "image_url": {
                                    "url":
                                        image_data_url
                                }
                            }
                        ]
                    }
                ],

                "temperature":
                    0.4,

                "max_tokens":
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "xAI IMAGE ANALYSIS STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "xAI IMAGE ANALYSIS FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "xAI image analysis received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "xAI IMAGE ANALYSIS ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# GROQ - IMAGE UNDERSTANDING
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

    try:

        print(
            "Trying Groq with image..."
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
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
                                        image_data_url
                                }
                            }
                        ]
                    }
                ],

                "temperature":
                    0.4,

                "max_completion_tokens":
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq IMAGE ANALYSIS STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq IMAGE ANALYSIS FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "Groq image analysis received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "Groq IMAGE ANALYSIS ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# MISTRAL - IMAGE UNDERSTANDING
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

    try:

        print(
            "Trying Mistral with image..."
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
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
                                        image_data_url
                                }
                            }
                        ]
                    }
                ],

                "temperature":
                    0.4,

                "max_tokens":
                    MAX_TOKENS
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral IMAGE ANALYSIS STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral IMAGE ANALYSIS FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "Mistral image analysis received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "Mistral IMAGE ANALYSIS ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# OPENROUTER - IMAGE UNDERSTANDING
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

    try:

        print(
            "Trying OpenRouter with image..."
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        response = requests.post(
            OPENROUTER_CHAT_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "X-Title":
                    "Ido AI"
            },

            json={
                "model":
                    OPENROUTER_MODEL,

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
                                        image_data_url
                                }
                            }
                        ]
                    }
                ]
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "OpenRouter IMAGE ANALYSIS STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter IMAGE ANALYSIS FAILED:",
                response.text[:1000]
            )

            return None

        answer = extract_chat_answer(
            response.json()
        )

        if answer:

            print(
                "OpenRouter image analysis received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "OpenRouter IMAGE ANALYSIS ERROR:",
            str(e)[:1000]
        )

        return None


# =========================================================
# GET IMAGE RESPONSE
# =========================================================

def get_image_response(
    message,
    image_bytes,
    mime_type
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

    if (
        not message
        or not message.strip()
    ):

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    message = message.strip()


    # -----------------------------------------------------
    # 1. GEMINI
    # -----------------------------------------------------

    if gemini_client is not None:

        try:

            print(
                "Trying Gemini with image..."
            )

            image_base64 = base64.b64encode(
                image_bytes
            ).decode(
                "utf-8"
            )

            response = (
                gemini_client.models.generate_content(
                    model=GEMINI_MODEL,

                    contents=[
                        message,
                        {
                            "mime_type":
                                mime_type,

                            "data":
                                image_base64
                        }
                    ]
                )
            )

            if response:

                answer = clean_answer(
                    response.text
                )

                if answer:

                    print(
                        "Gemini image analysis received."
                    )

                    return answer

        except Exception as e:

            print(
                "Gemini image FAILED:",
                str(e)[:1000]
            )


    # -----------------------------------------------------
    # 2. XAI / GROK
    # -----------------------------------------------------

    answer = ask_xai_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:
        return answer


    # -----------------------------------------------------
    # 3. GROQ
    # -----------------------------------------------------

    answer = ask_groq_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:
        return answer


    # -----------------------------------------------------
    # 4. MISTRAL
    # -----------------------------------------------------

    answer = ask_mistral_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:
        return answer


    # -----------------------------------------------------
    # 5. OPENROUTER
    # -----------------------------------------------------

    answer = ask_openrouter_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:
        return answer


    return (
        "تعذر تحليل الصورة حاليًا."
    )


# =========================================================
# QUICK / STATIC RESPONSES
# =========================================================

def get_static_response(
    message_lower
):

    responses = {

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

        "من هو مطورك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من برمجك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من اخترعك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من أنشأك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صممك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صاحبك":
            "أنا Ido AI، وقد تم تطويري "
            "وبنائي بواسطة Noufal Ouhadi.",

        "من وراءك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صنع ido ai":
            "تم تطوير Ido AI وبناؤه "
            "بواسطة Noufal Ouhadi.",

        "من طور ido ai":
            "تم تطوير Ido AI بواسطة "
            "Noufal Ouhadi.",

        "الوقت":
            "يمكنك معرفة الوقت من النظام.",

        "ما هو الذكاء الاصطناعي":
            "الذكاء الاصطناعي هو مجال من علوم "
            "الحاسوب يهدف إلى تطوير أنظمة قادرة "
            "على فهم المعلومات والتعلم منها "
            "وتنفيذ مهام تحتاج عادةً إلى قدر "
            "من الذكاء البشري.",

        "ما هي بايثون":
            "Python هي لغة برمجة قوية وسهلة "
            "الاستخدام، وتُستخدم في تطوير "
            "البرامج والذكاء الاصطناعي "
            "وتحليل البيانات.",

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

    for key, value in responses.items():

        if key in message_lower:

            return value

    return None


# =========================================================
# TEXT ROUTER
# =========================================================

def get_text_response(
    message
):

    # -----------------------------------------------------
    # 1. GEMINI
    # -----------------------------------------------------

    answer = ask_gemini(
        message
    )

    if answer:

        return answer


    print(
        "Gemini failed. "
        "Trying xAI / Grok..."
    )


    # -----------------------------------------------------
    # 2. GROK
    # -----------------------------------------------------

    answer = ask_xai(
        message
    )

    if answer:

        return answer


    print(
        "Grok failed. "
        "Trying Groq..."
    )


    # -----------------------------------------------------
    # 3. GROQ
    # -----------------------------------------------------

    answer = ask_groq(
        message
    )

    if answer:

        return answer


    print(
        "Groq failed. "
        "Trying OpenRouter..."
    )


    # -----------------------------------------------------
    # 4. OPENROUTER
    # -----------------------------------------------------

    answer = ask_openrouter(
        message
    )

    if answer:

        return answer


    print(
        "OpenRouter failed. "
        "Trying Mistral..."
    )


    # -----------------------------------------------------
    # 5. MISTRAL
    # -----------------------------------------------------

    answer = ask_mistral(
        message
    )

    if answer:

        return answer


    return (
        "أنا Ido AI ولم أجد إجابة حاليًا."
    )


# =========================================================
# MAIN RESPONSE - DATA VERSION
# =========================================================

def get_response_data(
    message
):

    if not message:

        return {
            "answer":
                "اكتب رسالة أولًا.",

            "imageUrl":
                None
        }

    original_message = str(
        message
    ).strip()

    if not original_message:

        return {
            "answer":
                "اكتب رسالة أولًا.",

            "imageUrl":
                None
        }


    # =====================================================
    # IMAGE GENERATION
    # =====================================================

    if is_image_generation_request(
        original_message
    ):

        image_prompt = get_image_prompt(
            original_message
        )

        if not image_prompt:

            return {
                "answer":
                    "اكتب لي وصف الصورة "
                    "التي تريد إنشاءها.",

                "imageUrl":
                    None
            }


        print(
            "IMAGE GENERATION INTENT DETECTED:",
            original_message
        )

        print(
            "DIRECT IMAGE GENERATION REQUEST:",
            original_message
        )

        print(
            "FINAL IMAGE PROMPT:",
            image_prompt
        )


        image_url = generate_image(
            image_prompt
        )

        if image_url:

            return {
                "answer":
                    "تم إنشاء الصورة بنجاح. 🖼️",

                "imageUrl":
                    image_url
            }


        return {
            "answer":
                "تعذر إنشاء الصورة حاليًا. "
                "تمت تجربة Pollinations ثم xAI "
                "ثم OpenRouter، ولم يُرجع أي "
                "مولد صورة نتيجة صالحة.",

            "imageUrl":
                None
        }


    # =====================================================
    # STATIC RESPONSE
    # =====================================================

    static_answer = get_static_response(
        original_message.lower()
    )

    if static_answer:

        return {
            "answer":
                static_answer,

            "imageUrl":
                None
        }


    # =====================================================
    # NORMAL TEXT
    # =====================================================

    answer = get_text_response(
        original_message
    )

    return {
        "answer":
            answer,

        "imageUrl":
            None
    }


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================
#
# Existing app.py versions may call get_response()
# and expect a string.
#
# For image generation, the new frontend should use
# get_response_data() so it can receive imageUrl.
# =========================================================

def get_response(
    message
):

    result = get_response_data(
        message
    )

    if not isinstance(
        result,
        dict
    ):

        return str(
            result
        )

    return result.get(
        "answer",
        ""
    )


# =========================================================
# OPTIONAL HELPER
# =========================================================

def health_status():

    return {

        "gemini":
            bool(GEMINI_API_KEY),

        "xai":
            bool(XAI_API_KEY),

        "groq":
            bool(GROQ_API_KEY),

        "openrouter":
            bool(OPENROUTER_API_KEY),

        "pollinations":
            bool(POLLINATIONS_API_KEY),

        "mistral":
            bool(MISTRAL_API_KEY),

        "image_route":
            [
                "pollinations",
                "xai",
                "openrouter"
            ],

        "text_route":
            [
                "gemini",
                "xai",
                "groq",
                "openrouter",
                "mistral"
            ]
    }


# =========================================================
# END OF BRAIN.PY
# =========================================================

print(
    "BRAIN.PY READY."
)

print(
    "Fast failover enabled."
)

print(
    "Pollinations image generation enabled."
)

print(
    "================================================="
)