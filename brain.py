# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL SIMPLE PROVIDER ROUTING
#
# TEXT / CHAT:
#     MISTRAL ONLY
#
# IMAGE UNDERSTANDING:
#     GEMINI ONLY
#
# IMAGE GENERATION:
#     GEMINI ONLY
#
# IMAGE EDITING:
#     GEMINI ONLY
#
# NO:
#     XAI
#     GROQ
#     OPENROUTER
#
# ============================================================


import os
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

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# ============================================================
# MODELS
# ============================================================

# ------------------------------------------------------------
# MISTRAL - TEXT ONLY
# ------------------------------------------------------------

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-medium-latest"
)


# ------------------------------------------------------------
# GEMINI - TEXT MODEL
#
# Kept in ENV for compatibility.
# It is NOT used for normal chat.
# ------------------------------------------------------------

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash"
)


# ------------------------------------------------------------
# GEMINI - IMAGE
#
# Used for:
#     - image understanding
#     - image generation
#     - image editing
# ------------------------------------------------------------

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)


# ------------------------------------------------------------
# GEMINI IMAGE EDIT MODEL
# ------------------------------------------------------------

GEMINI_IMAGE_EDIT_MODEL = os.getenv(
    "GEMINI_IMAGE_EDIT_MODEL",
    GEMINI_IMAGE_MODEL
)


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


GEMINI_INTERACTIONS_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
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
    "GEMINI CLIENT:",
    "READY"
    if GEMINI_API_KEY
    else "DISABLED"
)

print("=" * 70)

print(
    "MISTRAL TEXT MODEL:",
    MISTRAL_TEXT_MODEL
)

print(
    "GEMINI TEXT MODEL:",
    GEMINI_TEXT_MODEL
)

print(
    "GEMINI IMAGE MODEL:",
    GEMINI_IMAGE_MODEL
)

print(
    "GEMINI IMAGE EDIT MODEL:",
    GEMINI_IMAGE_EDIT_MODEL
)

print("=" * 70)

print("""
FINAL PROVIDER ROUTING

TEXT:
    MISTRAL ONLY

IMAGE UNDERSTANDING:
    GEMINI ONLY

IMAGE GENERATION:
    GEMINI ONLY

IMAGE EDITING:
    GEMINI ONLY
""")

print("=" * 70)


# ============================================================
# HTTP HELPERS
# ============================================================

def _mistral_headers() -> dict:

    return {
        "Authorization":
            f"Bearer {MISTRAL_API_KEY}",

        "Content-Type":
            "application/json",
    }


def _gemini_headers() -> dict:

    return {
        "x-goog-api-key":
            GEMINI_API_KEY,

        "Content-Type":
            "application/json",
    }


def _safe_json(response) -> dict:

    try:

        data = response.json()

        if isinstance(
            data,
            dict
        ):
            return data

    except Exception:
        pass

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


    # ========================================================
    # OpenAI-compatible
    # ========================================================

    choices = data.get(
        "choices"
    )

    if isinstance(
        choices,
        list
    ) and choices:

        choice = choices[0]

        if isinstance(
            choice,
            dict
        ):

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


            text = choice.get(
                "text"
            )

            if isinstance(
                text,
                str
            ):
                return text.strip()


    # ========================================================
    # Gemini legacy structure
    # ========================================================

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


    # ========================================================
    # Gemini Interactions API
    # ========================================================

    output_text = data.get(
        "output_text"
    )

    if isinstance(
        output_text,
        str
    ):

        return output_text.strip()


    # ========================================================
    # Search through steps
    # ========================================================

    steps = data.get(
        "steps"
    )

    if isinstance(
        steps,
        list
    ):

        result = []

        for step in steps:

            if not isinstance(
                step,
                dict
            ):
                continue

            step_text = step.get(
                "text"
            )

            if isinstance(
                step_text,
                str
            ):
                result.append(
                    step_text
                )

            content = step.get(
                "content"
            )

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

                    text = item.get(
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


    return ""


# ============================================================
# GEMINI IMAGE EXTRACTION
# ============================================================

def _extract_gemini_image(
    data: Any
) -> Optional[str]:

    if not isinstance(
        data,
        dict
    ):
        return None


    # ========================================================
    # output_image
    # ========================================================

    output_image = data.get(
        "output_image"
    )

    if isinstance(
        output_image,
        dict
    ):

        image_data = output_image.get(
            "data"
        )

        if isinstance(
            image_data,
            str
        ) and image_data:

            mime_type = (
                output_image.get(
                    "mime_type"
                )
                or
                "image/png"
            )

            return (
                f"data:{mime_type};base64,"
                f"{image_data}"
            )


    # ========================================================
    # steps
    # ========================================================

    steps = data.get(
        "steps"
    )

    if isinstance(
        steps,
        list
    ):

        for step in steps:

            if not isinstance(
                step,
                dict
            ):
                continue


            content = step.get(
                "content"
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


                # ------------------------------------------------
                # Direct data
                # ------------------------------------------------

                image_data = item.get(
                    "data"
                )

                if isinstance(
                    image_data,
                    str
                ) and image_data:

                    item_type = item.get(
                        "type",
                        ""
                    )

                    if (
                        item_type == "image"
                        or
                        item.get(
                            "mime_type"
                        )
                    ):

                        mime_type = (
                            item.get(
                                "mime_type"
                            )
                            or
                            "image/png"
                        )

                        return (
                            f"data:{mime_type};base64,"
                            f"{image_data}"
                        )


                # ------------------------------------------------
                # Inline data
                # ------------------------------------------------

                inline_data = item.get(
                    "inline_data"
                )

                if isinstance(
                    inline_data,
                    dict
                ):

                    encoded = inline_data.get(
                        "data"
                    )

                    if isinstance(
                        encoded,
                        str
                    ) and encoded:

                        mime_type = (
                            inline_data.get(
                                "mime_type"
                            )
                            or
                            "image/png"
                        )

                        return (
                            f"data:{mime_type};base64,"
                            f"{encoded}"
                        )


    # ========================================================
    # Legacy Gemini parts
    # ========================================================

    candidates = data.get(
        "candidates"
    )

    if isinstance(
        candidates,
        list
    ):

        for candidate in candidates:

            if not isinstance(
                candidate,
                dict
            ):
                continue

            content = candidate.get(
                "content",
                {}
            )

            if not isinstance(
                content,
                dict
            ):
                continue

            parts = content.get(
                "parts",
                []
            )

            if not isinstance(
                parts,
                list
            ):
                continue

            for part in parts:

                if not isinstance(
                    part,
                    dict
                ):
                    continue

                inline_data = part.get(
                    "inlineData"
                )

                if not inline_data:
                    inline_data = part.get(
                        "inline_data"
                    )

                if isinstance(
                    inline_data,
                    dict
                ):

                    encoded = inline_data.get(
                        "data"
                    )

                    if encoded:

                        mime_type = (
                            inline_data.get(
                                "mimeType"
                            )
                            or
                            inline_data.get(
                                "mime_type"
                            )
                            or
                            "image/png"
                        )

                        return (
                            f"data:{mime_type};base64,"
                            f"{encoded}"
                        )


    return None


# ============================================================
# IMAGE -> BASE64
# ============================================================

def _image_to_base64(
    image_bytes: bytes
) -> str:

    return base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


# ============================================================
# MISTRAL TEXT
# ============================================================

def _mistral_text(
    message: str
) -> Optional[str]:

    if not MISTRAL_API_KEY:

        print(
            "MISTRAL TEXT: API KEY DISABLED"
        )

        return None


    print(
        "TEXT PROVIDER: MISTRAL"
    )


    payload = {

        "model":
            MISTRAL_TEXT_MODEL,

        "messages": [

            {
                "role":
                    "system",

                "content":
                    (
                        "You are IDO AI. "
                        "Answer naturally, accurately "
                        "and helpfully. "
                        "Use the same language as the user. "
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

        "max_tokens":
            4096,
    }


    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        try:

            response = requests.post(

                f"{MISTRAL_BASE_URL}"
                "/chat/completions",

                headers=
                    _mistral_headers(),

                json=
                    payload,

                timeout=
                    AI_REQUEST_TIMEOUT,
            )


            if response.status_code == 429:

                if (
                    attempt
                    >=
                    MISTRAL_MAX_RETRIES
                ):

                    print(
                        "MISTRAL RATE LIMIT"
                    )

                    return None


                delay = (
                    MISTRAL_RETRY_BASE_SECONDS
                    *
                    (
                        2 ** attempt
                    )
                )

                print(
                    "MISTRAL RATE LIMIT - "
                    f"WAIT {delay}s"
                )

                import time

                time.sleep(
                    delay
                )

                continue


            if response.status_code >= 400:

                print(
                    "MISTRAL TEXT ERROR:",
                    response.status_code,
                    response.text[:1000],
                )

                return None


            text = _extract_text(
                _safe_json(
                    response
                )
            )


            if text:

                return text


            print(
                "MISTRAL RETURNED EMPTY RESPONSE"
            )

            return None


        except Exception as exc:

            print(
                "MISTRAL TEXT EXCEPTION:",
                repr(exc)
            )

            return None


    return None


# ============================================================
# GEMINI IMAGE REQUEST
# ============================================================

def _gemini_image_request(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[dict]:

    if not GEMINI_API_KEY:

        print(
            "GEMINI IMAGE: API KEY DISABLED"
        )

        return None


    model = (
        model
        or
        GEMINI_IMAGE_MODEL
    )


    print("=" * 70)

    print(
        "GEMINI IMAGE REQUEST"
    )

    print(
        "MODEL:",
        model
    )

    print(
        "HAS INPUT IMAGE:",
        bool(image_bytes)
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 70)


    # ========================================================
    # INPUT
    # ========================================================

    inputs = []


    # --------------------------------------------------------
    # Existing image
    # --------------------------------------------------------

    if image_bytes:

        encoded = _image_to_base64(
            image_bytes
        )

        inputs.append({

            "type":
                "image",

            "mime_type":
                mime_type
                or
                "image/png",

            "data":
                encoded,
        })


    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    inputs.append({

        "type":
            "text",

        "text":
            prompt,
    })


    # ========================================================
    # PAYLOAD
    # ========================================================

    payload = {

        "model":
            model,

        "input":
            inputs,

        "response_format": {

            "type":
                "image",

            "mime_type":
                "image/png",

            "aspect_ratio":
                "1:1",

            "image_size":
                "1K",
        },
    }


    # ========================================================
    # REQUEST
    # ========================================================

    try:

        response = requests.post(

            GEMINI_INTERACTIONS_URL,

            headers=
                _gemini_headers(),

            json=
                payload,

            timeout=
                AI_REQUEST_TIMEOUT,
        )


        if response.status_code >= 400:

            print(
                "GEMINI IMAGE ERROR:",
                response.status_code,
                response.text[:2000],
            )

            return None


        data = _safe_json(
            response
        )


        image_url = _extract_gemini_image(
            data
        )


        text = _extract_text(
            data
        )


        if image_url:

            print(
                "GEMINI IMAGE SUCCESS"
            )

            return {

                "imageUrl":
                    image_url,

                "answer":
                    text
                    or
                    "تم إنشاء الصورة بنجاح.",

                "provider":
                    "Gemini",
            }


        print(
            "GEMINI IMAGE RESPONSE "
            "DID NOT CONTAIN IMAGE"
        )

        print(
            "RESPONSE:",
            str(data)[:3000]
        )


    except Exception as exc:

        print(
            "GEMINI IMAGE EXCEPTION:",
            repr(exc)
        )


    return None


# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================

def _gemini_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    if not GEMINI_API_KEY:

        print(
            "GEMINI VISION: API KEY DISABLED"
        )

        return None


    print("=" * 70)

    print(
        "GEMINI IMAGE UNDERSTANDING"
    )

    print(
        "MODEL:",
        GEMINI_IMAGE_MODEL
    )

    print("=" * 70)


    encoded = _image_to_base64(
        image_bytes
    )


    payload = {

        "model":
            GEMINI_IMAGE_MODEL,

        "input": [

            {
                "type":
                    "image",

                "mime_type":
                    mime_type,

                "data":
                    encoded,
            },

            {
                "type":
                    "text",

                "text":
                    (
                        message
                        or
                        "حلل هذه الصورة واشرح لي "
                        "ما الذي يظهر فيها بالتفصيل."
                    ),
            },
        ],

        "response_format": [

            {
                "type":
                    "text"
            }
        ],
    }


    try:

        response = requests.post(

            GEMINI_INTERACTIONS_URL,

            headers=
                _gemini_headers(),

            json=
                payload,

            timeout=
                AI_REQUEST_TIMEOUT,
        )


        if response.status_code >= 400:

            print(
                "GEMINI VISION ERROR:",
                response.status_code,
                response.text[:2000],
            )

            return None


        data = _safe_json(
            response
        )


        text = _extract_text(
            data
        )


        if text:

            print(
                "GEMINI VISION SUCCESS"
            )

            return text


        print(
            "GEMINI VISION EMPTY RESPONSE"
        )


    except Exception as exc:

        print(
            "GEMINI VISION EXCEPTION:",
            repr(exc)
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


    text = message.lower().strip()


    words = [

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


    return any(
        word in text
        for word in words
    )


# ============================================================
# IMAGE EDIT DETECTOR
# ============================================================

def is_image_edit_request(
    message: str
) -> bool:

    if not message:
        return False


    text = message.lower()


    words = [

        "عدل الصورة",
        "عدل الصوره",

        "تعديل الصورة",
        "تعديل الصوره",

        "حرر الصورة",
        "حرر الصوره",

        "غير الصورة",
        "غير الصوره",

        "غيّر الصورة",
        "غيّر الصوره",

        "edit image",
        "edit the image",

        "modify image",
        "modify the image",

        "change the image",

        "transform the image",
    ]


    return any(
        word in text
        for word in words
    )


# ============================================================
# GENERATE IMAGE
# ============================================================

def generate_image(
    prompt: str
) -> Optional[str]:

    result = _gemini_image_request(

        prompt=prompt,

        image_bytes=None,

        mime_type=None,

        model=
            GEMINI_IMAGE_MODEL,
    )


    if result:

        return result.get(
            "imageUrl"
        )


    return None


# ============================================================
# EDIT IMAGE
# ============================================================

def edit_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    result = _gemini_image_request(

        prompt=prompt,

        image_bytes=image_bytes,

        mime_type=mime_type,

        model=
            GEMINI_IMAGE_EDIT_MODEL,
    )


    if result:

        return result.get(
            "imageUrl"
        )


    return None


# ============================================================
# GET IMAGE RESPONSE
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
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 70)


    # ========================================================
    # 1. EDIT EXISTING IMAGE
    # ========================================================

    if (
        image_bytes
        and
        is_image_edit_request(
            message
        )
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

                "provider":
                    "Gemini",

                "conversation_id":
                    conversation_id,
            }


        return {

            "answer":
                "تعذر تعديل الصورة حاليًا عبر Gemini.",

            "imageUrl":
                "",

            "provider":
                "Gemini",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # 2. ANALYZE EXISTING IMAGE
    # ========================================================

    if image_bytes:

        result = _gemini_vision(

            message,

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

                "provider":
                    "Gemini",

                "conversation_id":
                    conversation_id,
            }


        return {

            "answer":
                "تعذر تحليل الصورة حاليًا عبر Gemini.",

            "imageUrl":
                "",

            "provider":
                "Gemini",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # 3. GENERATE IMAGE
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

            "provider":
                "Gemini",

            "conversation_id":
                conversation_id,
        }


    return {

        "answer":
            (
                "تعذر إنشاء الصورة حاليًا "
                "عبر Gemini."
            ),

        "imageUrl":
            "",

        "provider":
            "Gemini",

        "conversation_id":
            conversation_id,
    }


# ============================================================
# MAIN RESPONSE
# ============================================================

def get_response(
    message: str,
    conversation_id: Optional[str] = None,
):

    message = str(
        message or ""
    ).strip()


    if not message:

        return (
            "اكتب رسالة أولًا."
        )


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
    # IMAGE GENERATION FROM TEXT
    #
    # This is important because app.py sends normal text
    # requests through get_response().
    # ========================================================

    if is_image_request(
        message
    ):

        print(
            "IMAGE REQUEST DETECTED"
        )

        print(
            "IMAGE PROVIDER: GEMINI ONLY"
        )


        result = generate_image(
            message
        )


        if result:

            return {

                "answer":
                    "تم إنشاء الصورة بنجاح.",

                "imageUrl":
                    result,

                "provider":
                    "Gemini",

                "conversation_id":
                    conversation_id,
            }


        return {

            "answer":
                "تعذر إنشاء الصورة حاليًا عبر Gemini.",

            "imageUrl":
                "",

            "provider":
                "Gemini",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # NORMAL TEXT
    # ========================================================

    result = _mistral_text(
        message
    )


    if result:

        return {

            "answer":
                result,

            "imageUrl":
                "",

            "provider":
                "Mistral",

            "conversation_id":
                conversation_id,
        }


    return {

        "answer":
            (
                "عذرًا، لم أتمكن من الحصول "
                "على إجابة من Mistral حاليًا."
            ),

        "imageUrl":
            "",

        "provider":
            "Mistral",

        "conversation_id":
            conversation_id,
    }


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message: str,
) -> str:

    result = get_response(
        message
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


    return (
        "لم أتمكن من الحصول "
        "على إجابة حاليًا."
    )


# ============================================================
# COMPATIBILITY
# ============================================================

def ask_ollama(
    message: str,
) -> Optional[str]:

    """
    Ollama compatibility function.

    It is intentionally disabled in the
    final provider routing.
    """

    return None


# ============================================================
# PROVIDER STATUS
# ============================================================

def provider_status():

    return {

        "mistral":
            bool(
                MISTRAL_API_KEY
            ),

        "gemini":
            bool(
                GEMINI_API_KEY
            ),

        "text": [
            "mistral"
        ],

        "vision": [
            "gemini"
        ],

        "image": [
            "gemini"
        ],

        "image_edit": [
            "gemini"
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
print("IDO AI BRAIN READY")
print("=" * 70)