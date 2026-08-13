# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL TEST ROUTING
#
# TEXT:
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI 3.6
#
# IMAGES:
#     MISTRAL ONLY
#
#     ├── IMAGE UNDERSTANDING
#     ├── IMAGE GENERATION
#     └── IMAGE EDITING
#
# IMPORTANT:
#     XAI / GROK is NOT used in this version.
#
#     OpenRouter is NOT used for images.
#
#     Groq is NOT used for images.
#
# ============================================================

import os
import time
import base64
import logging
import re

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

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    os.getenv(
        "OPEN_ROUTER_API_KEY",
        ""
    )
).strip()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# ============================================================
# MODELS
# ============================================================

# ------------------------------------------------------------
# TEXT
# ------------------------------------------------------------

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


OPENROUTER_TEXT_MODEL = os.getenv(
    "OPENROUTER_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()


# ------------------------------------------------------------
# GEMINI
#
# IMPORTANT:
# Keep Gemini 3.6 as requested.
# ------------------------------------------------------------

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.6-flash"
).strip()


# ------------------------------------------------------------
# MISTRAL TEXT
#
# Mistral is NOT part of the text fallback chain
# in this test version.
# ------------------------------------------------------------


# ------------------------------------------------------------
# MISTRAL VISION
# ------------------------------------------------------------

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
).strip()


# ------------------------------------------------------------
# MISTRAL IMAGE
#
# Image generation is exposed by Mistral as the
# image_generation built-in tool.
#
# The model itself is configurable through ENV.
# ------------------------------------------------------------

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
).strip()


# ============================================================
# SETTINGS
# ============================================================

MISTRAL_MAX_RETRIES = int(
    os.getenv(
        "MISTRAL_MAX_RETRIES",
        "2"
    )
)

MISTRAL_RETRY_BASE_SECONDS = float(
    os.getenv(
        "MISTRAL_RETRY_BASE_SECONDS",
        "2"
    )
)

AI_REQUEST_TIMEOUT = int(
    os.getenv(
        "AI_REQUEST_TIMEOUT",
        "180"
    )
)


# ============================================================
# ENDPOINTS
# ============================================================

MISTRAL_BASE_URL = (
    "https://api.mistral.ai/v1"
)

GROQ_BASE_URL = (
    "https://api.groq.com/openai/v1"
)

OPENROUTER_BASE_URL = (
    "https://openrouter.ai/api/v1"
)

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
)


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)

print(
    "MISTRAL CLIENT:",
    "READY"
    if MISTRAL_API_KEY
    else "DISABLED"
)

print(
    "GROQ CLIENT:",
    "READY"
    if GROQ_API_KEY
    else "DISABLED"
)

print(
    "OPENROUTER CLIENT:",
    "READY"
    if OPENROUTER_API_KEY
    else "DISABLED"
)

print(
    "GEMINI CLIENT:",
    "READY"
    if GEMINI_API_KEY
    else "DISABLED"
)

print("=" * 70)

print(
    "GROQ TEXT MODEL:",
    GROQ_TEXT_MODEL
)

print(
    "OPENROUTER TEXT MODEL:",
    OPENROUTER_TEXT_MODEL
)

print(
    "GEMINI TEXT MODEL:",
    GEMINI_TEXT_MODEL
)

print(
    "MISTRAL VISION MODEL:",
    MISTRAL_VISION_MODEL
)

print(
    "MISTRAL IMAGE MODEL:",
    MISTRAL_IMAGE_MODEL
)

print("=" * 70)

print("FINAL PROVIDER ROUTING")

print(
    """
TEXT:
    GROQ
      ↓
    OPENROUTER
      ↓
    GEMINI 3.6
"""
)

print(
    """
IMAGES:
    MISTRAL ONLY

    ├── IMAGE UNDERSTANDING
    ├── IMAGE GENERATION
    └── IMAGE EDITING
"""
)

print("=" * 70)


# ============================================================
# HTTP HELPERS
# ============================================================

def _headers(
    api_key: str
) -> dict:

    return {
        "Authorization":
            f"Bearer {api_key}",

        "Content-Type":
            "application/json",
    }


def _post(
    url: str,
    headers: dict,
    payload: dict,
    timeout: Optional[int] = None,
):

    timeout = (
        timeout
        or
        AI_REQUEST_TIMEOUT
    )

    return requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=timeout,
    )


def _safe_json(
    response
):

    try:

        return response.json()

    except Exception:

        return {}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def _extract_text(
    data: Any
) -> str:

    if not isinstance(
        data,
        dict
    ):

        return ""


    # --------------------------------------------------------
    # OpenAI-compatible APIs
    # --------------------------------------------------------

    choices = data.get(
        "choices"
    )

    if isinstance(
        choices,
        list
    ) and choices:

        choice = choices[0]

        if not isinstance(
            choice,
            dict
        ):

            return ""


        # ----------------------------------------------------
        # Standard message
        # ----------------------------------------------------

        message = choice.get(
            "message"
        )

        if isinstance(
            message,
            dict
        ):

            content = message.get(
                "content"
            )

            if isinstance(
                content,
                str
            ):

                return content.strip()


            # ------------------------------------------------
            # Content array
            # ------------------------------------------------

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

                    return "\n".join(
                        parts
                    ).strip()


        # ----------------------------------------------------
        # Legacy text
        # ----------------------------------------------------

        text = choice.get(
            "text"
        )

        if isinstance(
            text,
            str
        ):

            return text.strip()


    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    candidates = data.get(
        "candidates"
    )

    if isinstance(
        candidates,
        list
    ) and candidates:

        candidate = candidates[0]

        if isinstance(
            candidate,
            dict
        ):

            content = candidate.get(
                "content",
                {}
            )

            if isinstance(
                content,
                dict
            ):

                parts = content.get(
                    "parts",
                    []
                )

                if isinstance(
                    parts,
                    list
                ):

                    result = []

                    for part in parts:

                        if not isinstance(
                            part,
                            dict
                        ):

                            continue

                        text = part.get(
                            "text"
                        )

                        if text:

                            result.append(
                                str(text)
                            )

                    if result:

                        return "\n".join(
                            result
                        ).strip()


    # --------------------------------------------------------
    # Alternate output_text
    # --------------------------------------------------------

    output_text = data.get(
        "output_text"
    )

    if isinstance(
        output_text,
        str
    ):

        return output_text.strip()


    return ""


# ============================================================
# IMAGE URL EXTRACTION
# ============================================================

def _extract_image_url(
    data: Any
) -> Optional[str]:

    if not data:

        return None


    # --------------------------------------------------------
    # Recursive URL finder
    # --------------------------------------------------------

    def recursive_find(
        obj
    ):

        if isinstance(
            obj,
            str
        ):

            text = obj.strip()

            # Direct HTTP URL
            if text.startswith(
                "https://"
            ):

                return text

            if text.startswith(
                "http://"
            ):

                return text

            # ------------------------------------------------
            # Search URLs embedded in text
            # ------------------------------------------------

            match = re.search(
                r'https?://[^\s\]\)\}"\']+',
                text
            )

            if match:

                return match.group(0).rstrip(
                    ".,;:!?)]}"
                )

            return None


        if isinstance(
            obj,
            dict
        ):

            # Most common keys first
            for key in (
                "url",
                "image_url",
                "imageUrl",
                "public_url",
                "file_url",
                "fileUrl",
                "signed_url",
                "signedUrl",
            ):

                value = obj.get(
                    key
                )

                found = recursive_find(
                    value
                )

                if found:

                    return found


            # Search all values
            for value in obj.values():

                found = recursive_find(
                    value
                )

                if found:

                    return found


        elif isinstance(
            obj,
            list
        ):

            for value in obj:

                found = recursive_find(
                    value
                )

                if found:

                    return found


        return None


    return recursive_find(
        data
    )


# ============================================================
# IMAGE BYTES -> DATA URL
# ============================================================

def _image_to_data_url(
    image_bytes: bytes,
    mime_type: Optional[str],
) -> str:

    mime_type = (
        mime_type
        or
        "image/png"
    )

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ============================================================
# GROQ TEXT
# ============================================================

def _groq_text(
    message: str
) -> Optional[str]:

    if not GROQ_API_KEY:

        return None


    print(
        "TEXT PROVIDER: GROQ"
    )


    payload = {

        "model":
            GROQ_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    (
                        "You are IDO AI. "
                        "Answer naturally, accurately, "
                        "and helpfully. "
                        "Use the user's language. "
                        "You can communicate in Arabic, "
                        "Moroccan Darija, French and English."
                    ),
            },

            {
                "role":
                    "user",

                "content":
                    message,
            },
        ],
    }


    try:

        response = _post(

            f"{GROQ_BASE_URL}"
            "/chat/completions",

            _headers(
                GROQ_API_KEY
            ),

            payload,
        )


        if response.status_code >= 400:

            print(
                "GROQ TEXT ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None


        return (
            _extract_text(
                _safe_json(response)
            )
            or
            None
        )


    except Exception as exc:

        print(
            "GROQ TEXT EXCEPTION:",
            repr(exc)
        )

        return None


# ============================================================
# OPENROUTER TEXT
# ============================================================

def _openrouter_text(
    message: str
) -> Optional[str]:

    if not OPENROUTER_API_KEY:

        return None


    print(
        "TEXT PROVIDER: OPENROUTER"
    )


    payload = {

        "model":
            OPENROUTER_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    (
                        "You are IDO AI. "
                        "Answer naturally, accurately, "
                        "and helpfully. "
                        "Use the user's language."
                    ),
            },

            {
                "role":
                    "user",

                "content":
                    message,
            },
        ],
    }


    try:

        response = _post(

            f"{OPENROUTER_BASE_URL}"
            "/chat/completions",

            _headers(
                OPENROUTER_API_KEY
            ),

            payload,
        )


        if response.status_code >= 400:

            print(
                "OPENROUTER TEXT ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None


        return (
            _extract_text(
                _safe_json(response)
            )
            or
            None
        )


    except Exception as exc:

        print(
            "OPENROUTER TEXT EXCEPTION:",
            repr(exc)
        )

        return None


# ============================================================
# GEMINI TEXT
# ============================================================

def _gemini_text(
    message: str
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print(
        "TEXT PROVIDER: GEMINI 3.6"
    )


    url = (

        f"{GEMINI_BASE_URL}/models/"
        f"{GEMINI_TEXT_MODEL}"
        ":generateContent"
        f"?key={GEMINI_API_KEY}"
    )


    payload = {

        "contents": [

            {
                "role":
                    "user",

                "parts": [

                    {
                        "text":
                            message
                    }
                ],
            }
        ]
    }


    try:

        response = requests.post(

            url,

            headers={
                "Content-Type":
                    "application/json"
            },

            json=payload,

            timeout=
                AI_REQUEST_TIMEOUT,
        )


        if response.status_code >= 400:

            print(
                "GEMINI ERROR:",
                response.status_code,
                response.text[:500],
            )

            return None


        return (
            _extract_text(
                _safe_json(response)
            )
            or
            None
        )


    except Exception as exc:

        print(
            "GEMINI EXCEPTION:",
            repr(exc)
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

        print(
            "MISTRAL VISION: API KEY DISABLED"
        )

        return None


    print("=" * 70)
    print(
        "MISTRAL IMAGE UNDERSTANDING"
    )
    print(
        "MODEL:",
        MISTRAL_VISION_MODEL
    )
    print("=" * 70)


    image_data_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )


    payload = {

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

                        "image_url":
                            image_data_url,
                    },
                ],
            }
        ],

        "max_tokens":
            4096,
    }


    try:

        response = _post(

            f"{MISTRAL_BASE_URL}"
            "/chat/completions",

            _headers(
                MISTRAL_API_KEY
            ),

            payload,
        )


        if response.status_code >= 400:

            print(
                "MISTRAL VISION ERROR:",
                response.status_code,
                response.text[:1000],
            )

            return None


        text = _extract_text(
            _safe_json(response)
        )


        if text:

            print(
                "MISTRAL VISION SUCCESS"
            )

            return text


    except Exception as exc:

        print(
            "MISTRAL VISION EXCEPTION:",
            repr(exc)
        )


    return None


# ============================================================
# MISTRAL IMAGE GENERATION
# ============================================================

def _mistral_image(
    prompt: str
) -> Optional[str]:

    if not MISTRAL_API_KEY:

        print(
            "MISTRAL IMAGE: API KEY DISABLED"
        )

        return None


    print("=" * 70)
    print(
        "MISTRAL IMAGE GENERATION"
    )
    print(
        "MODEL:",
        MISTRAL_IMAGE_MODEL
    )
    print(
        "PROMPT:",
        prompt
    )
    print("=" * 70)


    payload = {

        "model":
            MISTRAL_IMAGE_MODEL,

        "messages": [

            {
                "role":
                    "user",

                "content":
                    prompt,
            }
        ],

        "tools": [

            {
                "type":
                    "image_generation"
            }
        ],
    }


    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        try:

            print(
                "MISTRAL IMAGE ATTEMPT:",
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}"
            )


            response = _post(

                f"{MISTRAL_BASE_URL}"
                "/chat/completions",

                _headers(
                    MISTRAL_API_KEY
                ),

                payload,
            )


            # ------------------------------------------------
            # Rate limit
            # ------------------------------------------------

            if response.status_code == 429:

                if (
                    attempt
                    >=
                    MISTRAL_MAX_RETRIES
                ):

                    print(
                        "MISTRAL IMAGE:"
                        " RATE LIMIT EXHAUSTED"
                    )

                    return None


                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )


                try:

                    delay = (
                        float(
                            retry_after
                        )
                        if retry_after
                        else
                        (
                            MISTRAL_RETRY_BASE_SECONDS
                            *
                            (2 ** attempt)
                        )
                    )

                except Exception:

                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        *
                        (2 ** attempt)
                    )


                delay = min(
                    delay,
                    30
                )


                print(
                    "MISTRAL IMAGE RATE LIMIT."
                    f" Sleeping {delay}s"
                )


                time.sleep(
                    delay
                )

                continue


            # ------------------------------------------------
            # Other errors
            # ------------------------------------------------

            if response.status_code >= 400:

                print(
                    "MISTRAL IMAGE ERROR:",
                    response.status_code,
                    response.text[:1500],
                )

                return None


            data = _safe_json(
                response
            )


            # ------------------------------------------------
            # Search complete response
            # ------------------------------------------------

            image_url = (
                _extract_image_url(
                    data
                )
            )


            if image_url:

                print(
                    "MISTRAL IMAGE SUCCESS:"
                )

                print(
                    image_url
                )

                return image_url


            # ------------------------------------------------
            # Some Mistral tool responses place the
            # generated image inside choices/messages/content.
            # The recursive extractor above searches all
            # nested structures, including those fields.
            # ------------------------------------------------

            text = _extract_text(
                data
            )


            if text:

                image_url = (
                    _extract_image_url(
                        text
                    )
                )

                if image_url:

                    print(
                        "MISTRAL IMAGE URL "
                        "FOUND IN TEXT"
                    )

                    return image_url


            print(
                "MISTRAL IMAGE:"
                " NO IMAGE URL FOUND"
            )

            print(
                "RAW RESPONSE:",
                str(data)[:2000]
            )

            return None


        except Exception as exc:

            print(
                "MISTRAL IMAGE EXCEPTION:",
                repr(exc)
            )

            if (
                attempt
                >=
                MISTRAL_MAX_RETRIES
            ):

                return None


            delay = min(

                MISTRAL_RETRY_BASE_SECONDS
                *
                (2 ** attempt),

                30
            )


            time.sleep(
                delay
            )


    return None


# ============================================================
# MISTRAL IMAGE EDITING
# ============================================================
#
# Important:
#
# The current Mistral API documents image generation through
# the image_generation built-in tool. Vision supports receiving
# the uploaded image.
#
# For this test version we send the uploaded image + edit
# instruction to Mistral's multimodal model and request the
# image-generation tool.
#
# The API decides whether the tool can produce the requested
# edited result.
# ============================================================

def _mistral_image_edit(
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not MISTRAL_API_KEY:

        print(
            "MISTRAL IMAGE EDIT:"
            " API KEY DISABLED"
        )

        return None


    print("=" * 70)
    print(
        "MISTRAL IMAGE EDIT"
    )
    print(
        "MODEL:",
        MISTRAL_IMAGE_MODEL
    )
    print(
        "PROMPT:",
        prompt
    )
    print("=" * 70)


    image_data_url = _image_to_data_url(
        image_bytes,
        mime_type,
    )


    payload = {

        "model":
            MISTRAL_IMAGE_MODEL,

        "messages": [

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            (
                                "Edit the provided image "
                                "according to this instruction: "
                                f"{prompt}"
                            ),
                    },

                    {
                        "type":
                            "image_url",

                        "image_url":
                            image_data_url,
                    },
                ],
            }
        ],

        "tools": [

            {
                "type":
                    "image_generation"
            }
        ],
    }


    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        try:

            print(
                "MISTRAL EDIT ATTEMPT:",
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}"
            )


            response = _post(

                f"{MISTRAL_BASE_URL}"
                "/chat/completions",

                _headers(
                    MISTRAL_API_KEY
                ),

                payload,
            )


            if response.status_code == 429:

                if (
                    attempt
                    >=
                    MISTRAL_MAX_RETRIES
                ):

                    return None


                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )


                try:

                    delay = (
                        float(
                            retry_after
                        )
                        if retry_after
                        else
                        (
                            MISTRAL_RETRY_BASE_SECONDS
                            *
                            (2 ** attempt)
                        )
                    )

                except Exception:

                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        *
                        (2 ** attempt)
                    )


                delay = min(
                    delay,
                    30
                )


                time.sleep(
                    delay
                )

                continue


            if response.status_code >= 400:

                print(
                    "MISTRAL IMAGE EDIT ERROR:",
                    response.status_code,
                    response.text[:1500],
                )

                return None


            data = _safe_json(
                response
            )


            image_url = (
                _extract_image_url(
                    data
                )
            )


            if image_url:

                print(
                    "MISTRAL IMAGE EDIT SUCCESS"
                )

                return image_url


            print(
                "MISTRAL IMAGE EDIT:"
                " NO IMAGE URL FOUND"
            )

            print(
                "RAW RESPONSE:",
                str(data)[:2000]
            )

            return None


        except Exception as exc:

            print(
                "MISTRAL IMAGE EDIT EXCEPTION:",
                repr(exc)
            )

            if (
                attempt
                >=
                MISTRAL_MAX_RETRIES
            ):

                return None


            delay = min(

                MISTRAL_RETRY_BASE_SECONDS
                *
                (2 ** attempt),

                30
            )


            time.sleep(
                delay
            )


    return None


# ============================================================
# IMAGE REQUEST DETECTOR
# ============================================================

def is_image_request(
    message: str
) -> bool:

    if not message:

        return False


    text = (
        str(message)
        .lower()
        .strip()
    )


    image_words = [

        "صورة",
        "صوره",
        "صور",

        "أنشئ صورة",
        "انشئ صورة",

        "أنشئ صوره",
        "انشئ صوره",

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

        "change the image",
    ]


    return any(
        word in text
        for word in (
            image_words
            +
            edit_words
        )
    )


def is_image_edit_request(
    message: str
) -> bool:

    if not message:

        return False


    text = (
        str(message)
        .lower()
        .strip()
    )


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
# IMAGE GENERATION ROUTER
# ============================================================

def generate_image(
    prompt: str
) -> Optional[str]:

    print("=" * 70)
    print(
        "IMAGE GENERATION START"
    )
    print(
        "IMAGE PROVIDER: MISTRAL ONLY"
    )
    print(
        "PROMPT:",
        prompt
    )
    print("=" * 70)


    result = _mistral_image(
        prompt
    )


    if result:

        print(
            "IMAGE PROVIDER: MISTRAL"
        )

        return result


    print(
        "IMAGE GENERATION FAILED:"
        " MISTRAL"
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
    print(
        "IMAGE EDITING START"
    )
    print(
        "IMAGE PROVIDER: MISTRAL ONLY"
    )
    print("=" * 70)


    result = _mistral_image_edit(

        prompt,

        image_bytes,

        mime_type,
    )


    if result:

        print(
            "IMAGE EDIT PROVIDER: MISTRAL"
        )

        return result


    print(
        "IMAGE EDITING FAILED:"
        " MISTRAL"
    )

    return None


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
    print(
        "IMAGE PROVIDER: MISTRAL ONLY"
    )
    print("=" * 70)


    # ========================================================
    # 1. INPUT IMAGE EXISTS
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        if is_image_edit_request(
            message
        ):

            result = edit_image(

                message,

                image_bytes,

                mime_type
                or
                "image/png",
            )


            if result:

                return {

                    "answer":
                        "تم تعديل الصورة بنجاح.",

                    "imageUrl":
                        result,

                    "image_url":
                        result,

                    "provider":
                        "Mistral",

                    "type":
                        "image",

                    "conversation_id":
                        conversation_id,
                }


            return {

                "answer":
                    (
                        "تعذر تعديل الصورة "
                        "حاليًا عبر Mistral."
                    ),

                "imageUrl":
                    "",

                "image_url":
                    "",

                "provider":
                    "Mistral",

                "type":
                    "error",

                "conversation_id":
                    conversation_id,
            }


        # ----------------------------------------------------
        # UNDERSTANDING
        # ----------------------------------------------------

        question = (
            str(message)
            .strip()
        )


        if not question:

            question = (
                "حلل هذه الصورة واشرح لي "
                "بالتفصيل ما الذي يظهر فيها."
            )


        result = analyze_image(

            question,

            image_bytes,

            mime_type
            or
            "image/png",
        )


        if result:

            return {

                "answer":
                    result,

                "imageUrl":
                    "",

                "image_url":
                    "",

                "provider":
                    "Mistral",

                "type":
                    "vision",

                "conversation_id":
                    conversation_id,
            }


        return {

            "answer":
                (
                    "تعذر تحليل الصورة "
                    "حاليًا عبر Mistral."
                ),

            "imageUrl":
                "",

            "image_url":
                "",

            "provider":
                "Mistral",

            "type":
                "error",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # 2. NO INPUT IMAGE
    #    → GENERATE IMAGE
    # ========================================================

    result = generate_image(
        message
    )


    if result:

        return {

            "answer":
                "تم إنشاء الصورة بنجاح.",

            "imageUrl":
                result,

            "image_url":
                result,

            "provider":
                "Mistral",

            "type":
                "image",

            "conversation_id":
                conversation_id,
        }


    return {

        "answer":
            (
                "تعذر إنشاء الصورة "
                "حاليًا عبر Mistral."
            ),

        "imageUrl":
            "",

        "image_url":
            "",

        "provider":
            "Mistral",

        "type":
            "error",

        "conversation_id":
            conversation_id,
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
    print(
        "IMAGE UNDERSTANDING START"
    )
    print(
        "VISION PROVIDER: MISTRAL ONLY"
    )
    print("=" * 70)


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


    print(
        "IMAGE UNDERSTANDING FAILED:"
        " MISTRAL"
    )

    return None


# ============================================================
# MAIN TEXT RESPONSE
# ============================================================

def get_response(
    message: str,
    conversation_id: Optional[str] = None,
):

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


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Image requests from the normal text API are NOT handled
    # here. Uploaded images go through get_image_response().
    # --------------------------------------------------------


    providers = [

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

            result = provider(
                message
            )


            if result:

                print("=" * 70)

                print(
                    "API CHAT SUCCESS"
                )

                print(
                    "PROVIDER:",
                    provider_name
                )

                print("=" * 70)


                return {

                    "answer":
                        result,

                    "imageUrl":
                        "",

                    "image_url":
                        "",

                    "provider":
                        provider_name,

                    "conversation_id":
                        conversation_id,
                }


        except Exception as exc:

            print(
                f"{provider_name}"
                " PROVIDER ERROR:",
                repr(exc)
            )


    return {

        "answer":
            (
                "عذرًا، لم أتمكن من الحصول "
                "على إجابة من مزودي الذكاء "
                "الاصطناعي المتاحين حاليًا."
            ),

        "imageUrl":
            "",

        "image_url":
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
    message: str
) -> str:

    result = get_response(
        message,
        conversation_id=None,
    )


    if isinstance(
        result,
        str
    ):

        return result


    if isinstance(
        result,
        dict
    ):

        answer = result.get(
            "answer"
        )

        if answer:

            return str(
                answer
            )


        text = result.get(
            "text"
        )

        if text:

            return str(
                text
            )


        message_text = result.get(
            "message"
        )

        if message_text:

            return str(
                message_text
            )


    return (
        "لم أتمكن من الحصول "
        "على إجابة حاليًا."
    )


# ============================================================
# COMPATIBILITY ROUTER
# ============================================================

def ask_ollama(
    message: str
) -> Optional[str]:

    """
    Compatibility function.

    Ollama is not part of the final cloud
    provider routing.
    """

    ollama_url = os.getenv(
        "OLLAMA_URL",
        ""
    ).strip()


    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.1:8b"
    ).strip()


    if not ollama_url:

        return None


    try:

        response = requests.post(

            f"{ollama_url.rstrip('/')}"
            "/api/generate",

            json={

                "model":
                    ollama_model,

                "prompt":
                    message,

                "stream":
                    False,
            },

            timeout=
                AI_REQUEST_TIMEOUT,
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

        "mistral":
            bool(MISTRAL_API_KEY),

        "groq":
            bool(GROQ_API_KEY),

        "openrouter":
            bool(OPENROUTER_API_KEY),

        "gemini":
            bool(GEMINI_API_KEY),

        "text": [

            "groq",
            "openrouter",
            "gemini",
        ],

        "vision": [

            "mistral",
        ],

        "image": [

            "mistral",
        ],
    }


# ============================================================
# STARTUP COMPATIBILITY
# ============================================================

print(
    "COMPATIBILITY:"
    " quick_response available"
)

print(
    "COMPATIBILITY:"
    " get_response("
    "message, conversation_id=None)"
)

print(
    "COMPATIBILITY:"
    " get_image_response("
    "message, image_bytes, mime_type,"
    "conversation_id=None)"
)

print("=" * 70)
print(
    "IMAGE PROVIDER: MISTRAL ONLY"
)
print("=" * 70)