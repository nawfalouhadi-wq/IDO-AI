# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL SIMPLE PROVIDER ROUTING
#
# TEXT:
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

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-medium-latest"
).strip()


GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.6-flash"
).strip()


GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
).strip()


GEMINI_IMAGE_EDIT_MODEL = os.getenv(
    "GEMINI_IMAGE_EDIT_MODEL",
    GEMINI_IMAGE_MODEL
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

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
)


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("IDO AI BRAIN.PY LOADED")
print("=" * 70)

print("FINAL PROVIDER ROUTING")

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


def _safe_json(response):

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
    # OpenAI-compatible response
    # --------------------------------------------------------

    choices = data.get(
        "choices"
    )

    if (
        isinstance(
            choices,
            list
        )
        and
        choices
    ):

        choice = choices[0]

        if not isinstance(
            choice,
            dict
        ):
            return ""


        message = choice.get(
            "message",
            {}
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


    # --------------------------------------------------------
    # Gemini response
    # --------------------------------------------------------

    candidates = data.get(
        "candidates"
    )

    if (
        isinstance(
            candidates,
            list
        )
        and
        candidates
    ):

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


    return ""


# ============================================================
# IMAGE EXTRACTION
# ============================================================

def _extract_image(
    data: Any
) -> Optional[str]:

    if not isinstance(
        data,
        dict
    ):
        return None


    # --------------------------------------------------------
    # Search Gemini parts
    # --------------------------------------------------------

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


                # ........................................
                # inlineData
                # ........................................

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

                    b64 = inline_data.get(
                        "data"
                    )

                    mime = inline_data.get(
                        "mimeType"
                    )

                    if not mime:

                        mime = inline_data.get(
                            "mime_type"
                        )

                    if (
                        isinstance(
                            b64,
                            str
                        )
                        and
                        b64
                    ):

                        mime = (
                            mime
                            or
                            "image/jpeg"
                        )

                        return (
                            f"data:{mime};base64,{b64}"
                        )


                # ........................................
                # direct URL
                # ........................................

                for key in (
                    "url",
                    "image_url",
                    "public_url",
                    "file_url",
                ):

                    value = part.get(
                        key
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


    # --------------------------------------------------------
    # Generic recursive search
    # --------------------------------------------------------

    def recursive_find(
        obj
    ):

        if isinstance(
            obj,
            str
        ):

            if obj.startswith(
                "https://"
            ):

                return obj

            return None


        if isinstance(
            obj,
            dict
        ):

            for key in (
                "url",
                "image_url",
                "public_url",
                "file_url",
            ):

                value = obj.get(
                    key
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
# IMAGE -> DATA URL
# ============================================================

def _image_to_data_url(
    image_bytes: bytes,
    mime_type: Optional[str]
) -> str:

    mime_type = (
        mime_type
        or
        "image/jpeg"
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
# MISTRAL TEXT
# ============================================================

def _mistral_text(
    message: str
) -> Optional[str]:

    if not MISTRAL_API_KEY:

        print(
            "MISTRAL TEXT: DISABLED"
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
                "role": "system",

                "content":
                    (
                        "You are IDO AI. "
                        "Answer naturally, "
                        "accurately and helpfully. "
                        "Use the language of the user. "
                        "You can communicate in Arabic, "
                        "Moroccan Darija, French and English."
                    )
            },

            {
                "role": "user",
                "content": message
            }

        ],

        "max_tokens":
            4096
    }


    try:

        for attempt in range(
            MISTRAL_MAX_RETRIES + 1
        ):

            print(
                "MISTRAL REQUEST ATTEMPT:",
                f"{attempt + 1}/"
                f"{MISTRAL_MAX_RETRIES + 1}"
            )


            response = _post(

                f"{MISTRAL_BASE_URL}/chat/completions",

                _headers(
                    MISTRAL_API_KEY
                ),

                payload
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


                print(
                    "MISTRAL RATE LIMIT:",
                    f"sleeping {delay}s"
                )

                time.sleep(
                    delay
                )

                continue


            if response.status_code >= 400:

                print(
                    "MISTRAL TEXT ERROR:",
                    response.status_code,
                    response.text[:1000]
                )

                return None


            text = _extract_text(
                _safe_json(
                    response
                )
            )

            if text:

                return text


            return None


    except Exception as exc:

        print(
            "MISTRAL TEXT EXCEPTION:",
            repr(exc)
        )


    return None


# ============================================================
# GEMINI GENERATE CONTENT
# ============================================================

def _gemini_generate(
    model: str,
    contents: list,
    response_modalities: Optional[list] = None,
) -> Optional[dict]:

    if not GEMINI_API_KEY:

        print(
            "GEMINI: DISABLED"
        )

        return None


    url = (
        f"{GEMINI_BASE_URL}/models/"
        f"{model}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )


    payload = {

        "contents":
            contents
    }


    # --------------------------------------------------------
    # Only add modalities when requested.
    # --------------------------------------------------------

    if response_modalities:

        payload[
            "generationConfig"
        ] = {

            "responseModalities":
                response_modalities
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
                AI_REQUEST_TIMEOUT
        )


        if response.status_code >= 400:

            print(
                "GEMINI ERROR:",
                response.status_code,
                response.text[:2000]
            )

            return None


        return _safe_json(
            response
        )


    except Exception as exc:

        print(
            "GEMINI REQUEST EXCEPTION:",
            repr(exc)
        )

        return None


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def _gemini_image(
    prompt: str
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print("=" * 70)
    print("GEMINI IMAGE REQUEST")
    print(
        "MODEL:",
        GEMINI_IMAGE_MODEL
    )
    print(
        "PROMPT:",
        prompt
    )
    print("=" * 70)


    contents = [

        {
            "role": "user",

            "parts": [

                {
                    "text": prompt
                }

            ]
        }

    ]


    # ========================================================
    # IMPORTANT
    #
    # Gemini image output is requested as IMAGE.
    # We do NOT send response_format={"mime_type":"image/png"}.
    #
    # This avoids the previous 400 error.
    # ========================================================

    data = _gemini_generate(

        GEMINI_IMAGE_MODEL,

        contents,

        response_modalities=[
            "IMAGE"
        ]
    )


    if not data:

        return None


    image = _extract_image(
        data
    )


    if image:

        print(
            "GEMINI IMAGE SUCCESS"
        )

        return image


    print(
        "GEMINI IMAGE ERROR:"
        " No image data returned."
    )


    # Sometimes the model may return text
    # instead of an image.

    text = _extract_text(
        data
    )

    if text:

        print(
            "GEMINI IMAGE TEXT RESPONSE:",
            text[:1000]
        )


    return None


# ============================================================
# GEMINI IMAGE EDITING
# ============================================================

def _gemini_image_edit(
    prompt: str,
    image_bytes: bytes,
    mime_type: str
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print("=" * 70)
    print("GEMINI IMAGE EDIT REQUEST")
    print(
        "MODEL:",
        GEMINI_IMAGE_EDIT_MODEL
    )
    print(
        "PROMPT:",
        prompt
    )
    print("=" * 70)


    image_data_url = _image_to_data_url(
        image_bytes,
        mime_type
    )


    # --------------------------------------------------------
    # Gemini expects image data as inlineData.
    # --------------------------------------------------------

    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or
        "image/jpeg"
    )


    contents = [

        {
            "role": "user",

            "parts": [

                {
                    "text":
                        prompt
                },

                {
                    "inlineData": {

                        "mimeType":
                            safe_mime,

                        "data":
                            encoded
                    }
                }

            ]
        }

    ]


    data = _gemini_generate(

        GEMINI_IMAGE_EDIT_MODEL,

        contents,

        response_modalities=[
            "IMAGE"
        ]
    )


    if not data:

        return None


    image = _extract_image(
        data
    )


    if image:

        print(
            "GEMINI IMAGE EDIT SUCCESS"
        )

        return image


    print(
        "GEMINI IMAGE EDIT:"
        " No image returned."
    )


    return None


# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================

def _gemini_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print(
        "IMAGE UNDERSTANDING PROVIDER: GEMINI"
    )


    encoded = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    safe_mime = (
        mime_type
        or
        "image/jpeg"
    )


    contents = [

        {
            "role": "user",

            "parts": [

                {
                    "text":
                        message
                },

                {
                    "inlineData": {

                        "mimeType":
                            safe_mime,

                        "data":
                            encoded
                    }
                }

            ]
        }

    ]


    data = _gemini_generate(

        GEMINI_TEXT_MODEL,

        contents
    )


    if not data:

        return None


    text = _extract_text(
        data
    )


    if text:

        print(
            "GEMINI VISION SUCCESS"
        )

        return text


    return None


# ============================================================
# IMAGE REQUEST DETECTION
# ============================================================

def is_image_request(
    message: str
) -> bool:

    if not message:
        return False


    text = (
        message
        .lower()
        .strip()
    )


    image_words = [

        # Arabic

        "صورة",
        "صوره",
        "صور",

        "أنشئ صورة",
        "أنشئ صوره",
        "انشئ صورة",
        "انشئ صوره",

        "اعمل صورة",
        "اعمل صوره",

        "اصنع صورة",
        "اصنع صوره",

        "ارسم لي",
        "ارسم",

        "صمم لي",
        "صمم",

        "توليد صورة",
        "توليد صوره",

        # English

        "generate image",
        "generate a picture",
        "create image",
        "create a picture",
        "make an image",
        "make a picture",
        "draw",
        "image generation",
        "picture",

        # French

        "génère une image",
        "generer une image",
        "crée une image",
        "creer une image",

    ]


    return any(
        word in text
        for word in image_words
    )


# ============================================================
# IMAGE EDIT DETECTION
# ============================================================

def is_image_edit_request(
    message: str
) -> bool:

    if not message:
        return False


    text = (
        message
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

        "غير الصورة",
        "غير الصوره",

        "غيّر الصورة",
        "غيّر الصوره",

        "edit image",
        "edit the image",

        "modify image",
        "modify the image",

        "change the image",

        "edit picture",
        "modify picture",

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
    print("IMAGE GENERATION START")
    print(
        "IMAGE PROVIDER: GEMINI ONLY"
    )
    print("=" * 70)


    result = _gemini_image(
        prompt
    )


    if result:

        print(
            "IMAGE PROVIDER: GEMINI"
        )

        return result


    print(
        "IMAGE GENERATION FAILED:"
        " GEMINI"
    )

    return None


# ============================================================
# IMAGE EDIT ROUTER
# ============================================================

def edit_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg"
) -> Optional[str]:

    print("=" * 70)
    print("IMAGE EDITING START")
    print(
        "IMAGE EDIT PROVIDER: GEMINI ONLY"
    )
    print("=" * 70)


    result = _gemini_image_edit(

        prompt,

        image_bytes,

        mime_type
    )


    if result:

        print(
            "IMAGE EDIT PROVIDER: GEMINI"
        )

        return result


    print(
        "IMAGE EDITING FAILED:"
        " GEMINI"
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

    print("=" * 70)


    # ========================================================
    # IMAGE EDIT
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
            "image/jpeg"
        )


        if result:

            return {

                "answer":
                    "تم تعديل الصورة بنجاح.",

                "imageUrl":
                    result,

                "provider":
                    "Gemini",

                "type":
                    "image",

                "conversation_id":
                    conversation_id
            }


        return {

            "answer":
                "تعذر تعديل الصورة حاليًا عبر Gemini.",

            "imageUrl":
                "",

            "provider":
                "Gemini",

            "type":
                "error",

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # IMAGE UNDERSTANDING
    #
    # If an image was uploaded but the user is NOT asking
    # to edit it, analyze it with Gemini.
    # ========================================================

    if image_bytes:

        analysis = _gemini_vision(

            message
            or
            "حلل هذه الصورة واشرح لي ما الذي يظهر فيها.",

            image_bytes,

            mime_type
            or
            "image/jpeg"
        )


        if analysis:

            return {

                "answer":
                    analysis,

                "imageUrl":
                    "",

                "provider":
                    "Gemini",

                "type":
                    "vision",

                "conversation_id":
                    conversation_id
            }


        return {

            "answer":
                "تعذر تحليل الصورة حاليًا عبر Gemini.",

            "imageUrl":
                "",

            "provider":
                "Gemini",

            "type":
                "error",

            "conversation_id":
                conversation_id
        }


    # ========================================================
    # IMAGE GENERATION
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

            "type":
                "image",

            "conversation_id":
                conversation_id
        }


    return {

        "answer":
            "تعذر إنشاء الصورة حاليًا عبر Gemini.",

        "imageUrl":
            "",

        "provider":
            "Gemini",

        "type":
            "error",

        "conversation_id":
            conversation_id
    }


# ============================================================
# MAIN RESPONSE
# ============================================================

def get_response(
    message: str,
    conversation_id: Optional[str] = None,
):

    message = str(
        message
        or
        ""
    ).strip()


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


    if not message:

        return (
            "اكتب رسالة أولًا."
        )


    # ========================================================
    # IMPORTANT
    #
    # IMAGE REQUESTS ARE INTERCEPTED HERE.
    #
    # This prevents Mistral from answering:
    #
    # "نعم أستطيع إنشاء صورة..."
    #
    # Instead the request goes directly to Gemini Image.
    # ========================================================

    if is_image_request(
        message
    ):

        print("=" * 70)
        print(
            "IMAGE REQUEST DETECTED"
        )
        print(
            "IMAGE PROVIDER: GEMINI ONLY"
        )
        print("=" * 70)


        result = get_image_response(

            message,

            image_bytes=None,

            mime_type=None,

            conversation_id=
                conversation_id
        )


        return result


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
                conversation_id
        }


    return {

        "answer":
            "عذرًا، لم أتمكن من الحصول على إجابة من Mistral حاليًا.",

        "imageUrl":
            "",

        "provider":
            "Mistral",

        "conversation_id":
            conversation_id
    }


# ============================================================
# QUICK RESPONSE
# ============================================================

def quick_response(
    message: str
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
        "لم أتمكن من الحصول على إجابة حاليًا."
    )


# ============================================================
# COMPATIBILITY
# ============================================================

def ask_ollama(
    message: str
) -> Optional[str]:

    """
    Compatibility function only.

    Ollama is NOT part of the active routing.
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
        ]
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