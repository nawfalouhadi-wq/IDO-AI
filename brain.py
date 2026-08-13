# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# CURRENT TEST PROVIDER
#
# TEXT:
#     MISTRAL ONLY
#
# IMAGE UNDERSTANDING:
#     MISTRAL VISION ONLY
#
# IMAGE GENERATION:
#     DISABLED TEMPORARILY
#
# IMAGE EDITING:
#     DISABLED TEMPORARILY
#
# IMPORTANT:
#     لا يوجد MISTRAL_IMAGE_MODEL هنا.
#
#     نستخدم Mistral للنص وتحليل الصور فقط.
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
# API KEY
# ============================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
    ""
).strip()


# ============================================================
# MISTRAL MODELS
# ============================================================

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-medium-latest"
).strip()


MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest"
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
# ENDPOINT
# ============================================================

MISTRAL_BASE_URL = (
    "https://api.mistral.ai/v1"
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
    "MISTRAL TEXT MODEL:",
    MISTRAL_TEXT_MODEL
)

print(
    "MISTRAL VISION MODEL:",
    MISTRAL_VISION_MODEL
)

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

print("""
FINAL TEST PROVIDER ROUTING

TEXT:
    MISTRAL ONLY

IMAGE UNDERSTANDING:
    MISTRAL VISION ONLY

IMAGE GENERATION:
    DISABLED

IMAGE EDITING:
    DISABLED
""")

print("=" * 70)


# ============================================================
# HTTP HEADERS
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


# ============================================================
# HTTP POST
# ============================================================

def _post(
    url: str,
    headers: dict,
    payload: dict,
    timeout: Optional[int] = None,
):

    timeout = (
        timeout
        or AI_REQUEST_TIMEOUT
    )

    return requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=timeout,
    )


# ============================================================
# SAFE JSON
# ============================================================

def _safe_json(
    response
) -> dict:

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
# EXTRACT TEXT
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
    # CHAT COMPLETIONS
    # ========================================================

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


            # ------------------------------------------------
            # Normal string
            # ------------------------------------------------

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


    # ========================================================
    # OUTPUT TEXT
    # ========================================================

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
# IMAGE -> DATA URL
# ============================================================

def _image_to_data_url(
    image_bytes: bytes,
    mime_type: Optional[str],
) -> str:

    mime_type = (
        mime_type
        or "image/png"
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
            "MISTRAL TEXT:",
            "API KEY NOT CONFIGURED"
        )

        return None


    print("=" * 60)
    print("TEXT PROVIDER: MISTRAL")
    print(
        "MODEL:",
        MISTRAL_TEXT_MODEL
    )
    print(
        "MESSAGE:",
        message
    )
    print("=" * 60)


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


    # ========================================================
    # RETRIES
    # ========================================================

    for attempt in range(
        MISTRAL_MAX_RETRIES + 1
    ):

        try:

            print(
                "MISTRAL REQUEST ATTEMPT:",
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


            # =================================================
            # RATE LIMIT
            # =================================================

            if response.status_code == 429:

                print(
                    "MISTRAL RATE LIMIT"
                )


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

                    if retry_after:

                        delay = float(
                            retry_after
                        )

                    else:

                        delay = (
                            MISTRAL_RETRY_BASE_SECONDS
                            *
                            (
                                2 ** attempt
                            )
                        )

                except Exception:

                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        *
                        (
                            2 ** attempt
                        )
                    )


                delay = min(
                    delay,
                    30
                )


                print(
                    "WAITING:",
                    f"{delay}s"
                )


                import time

                time.sleep(
                    delay
                )

                continue


            # =================================================
            # OTHER API ERROR
            # =================================================

            if response.status_code >= 400:

                print(
                    "MISTRAL TEXT ERROR:",
                    response.status_code
                )

                print(
                    response.text[:1000]
                )

                return None


            # =================================================
            # SUCCESS
            # =================================================

            data = _safe_json(
                response
            )

            text = _extract_text(
                data
            )


            if text:

                print(
                    "MISTRAL TEXT SUCCESS"
                )

                return text


            print(
                "MISTRAL TEXT:",
                "EMPTY RESPONSE"
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
# MISTRAL VISION
# ============================================================

def _mistral_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str,
) -> Optional[str]:

    if not MISTRAL_API_KEY:

        print(
            "MISTRAL VISION:",
            "API KEY NOT CONFIGURED"
        )

        return None


    print("=" * 60)
    print("IMAGE UNDERSTANDING")
    print("VISION PROVIDER: MISTRAL")
    print(
        "MODEL:",
        MISTRAL_VISION_MODEL
    )
    print("=" * 60)


    image_url = _image_to_data_url(
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
                            {
                                "url":
                                    image_url
                            },
                    },
                ],
            },
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
                response.status_code
            )

            print(
                response.text[:1000]
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
                "MISTRAL VISION SUCCESS"
            )

            return text


        print(
            "MISTRAL VISION:",
            "EMPTY RESPONSE"
        )

        return None


    except Exception as exc:

        print(
            "MISTRAL VISION EXCEPTION:",
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


    return any(
        word in text
        for word in image_words
    )


# ============================================================
# IMAGE EDIT DETECTOR
# ============================================================

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
# IMAGE GENERATION
# ============================================================

def generate_image(
    prompt: str
) -> Optional[str]:

    print("=" * 60)
    print("IMAGE GENERATION REQUEST")
    print("=" * 60)

    print(
        "MISTRAL IMAGE GENERATION:",
        "DISABLED"
    )

    print(
        "REASON:",
        "No MISTRAL_IMAGE_MODEL configured."
    )

    print("=" * 60)

    return None


# ============================================================
# IMAGE EDITING
# ============================================================

def edit_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    print("=" * 60)
    print("IMAGE EDITING REQUEST")
    print("=" * 60)

    print(
        "MISTRAL IMAGE EDITING:",
        "DISABLED"
    )

    print(
        "REASON:",
        "No MISTRAL_IMAGE_MODEL configured."
    )

    print("=" * 60)

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
    print("IMAGE REQUEST")
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
    # UPLOADED IMAGE
    # ========================================================

    if image_bytes:

        # ----------------------------------------------------
        # If user explicitly asks to edit the image
        # ----------------------------------------------------

        if is_image_edit_request(
            message
        ):

            return {

                "type":
                    "error",

                "answer":
                    (
                        "تعديل الصور غير متاح "
                        "في نسخة الاختبار الحالية."
                    ),

                "imageUrl":
                    "",

                "provider":
                    "Mistral",

                "conversation_id":
                    conversation_id,
            }


        # ----------------------------------------------------
        # Analyze uploaded image
        # ----------------------------------------------------

        result = _mistral_vision(

            message
            or
            (
                "حلل هذه الصورة واشرح "
                "بالتفصيل ما الذي يظهر فيها."
            ),

            image_bytes,

            mime_type
            or
            "image/png",
        )


        if result:

            return {

                "type":
                    "text",

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

            "type":
                "error",

            "answer":
                (
                    "تعذر تحليل الصورة حاليًا "
                    "عبر Mistral."
                ),

            "imageUrl":
                "",

            "provider":
                "Mistral",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    if is_image_request(
        message
    ):

        return {

            "type":
                "error",

            "answer":
                (
                    "إنشاء الصور غير متاح "
                    "في نسخة الاختبار الحالية. "
                    "نحن نختبر Mistral للنص "
                    "وتحليل الصور فقط."
                ),

            "imageUrl":
                "",

            "provider":
                "Mistral",

            "conversation_id":
                conversation_id,
        }


    # ========================================================
    # NO IMAGE
    # ========================================================

    return {

        "type":
            "error",

        "answer":
            "لم يتم إرسال صورة.",

        "imageUrl":
            "",

        "provider":
            "Mistral",

        "conversation_id":
            conversation_id,
    }


# ============================================================
# IMAGE UNDERSTANDING PUBLIC FUNCTION
# ============================================================

def analyze_image(
    message: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> Optional[str]:

    print("=" * 70)
    print("IMAGE UNDERSTANDING START")
    print("PROVIDER: MISTRAL ONLY")
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
        "IMAGE UNDERSTANDING FAILED"
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
    print("DYNAMIC AI RESPONSE")
    print(
        "PROVIDER: MISTRAL ONLY"
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


    message = str(
        message or ""
    ).strip()


    if not message:

        return (
            "اكتب رسالة أولًا."
        )


    # ========================================================
    # MISTRAL ONLY
    # ========================================================

    result = _mistral_text(
        message
    )


    if result:

        print("=" * 70)
        print("API CHAT SUCCESS")
        print("PROVIDER: MISTRAL")
        print("=" * 70)

        return result


    # ========================================================
    # NO FALLBACK
    # ========================================================

    print("=" * 70)
    print("MISTRAL FAILED")
    print("NO FALLBACK PROVIDER")
    print("=" * 70)


    return (
        "عذرًا، لم أتمكن من الحصول "
        "على إجابة من Mistral حاليًا."
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


    if isinstance(
        result,
        str
    ):

        return result


    if isinstance(
        result,
        dict
    ):

        text = result.get(
            "text"
        )

        if text:

            return str(
                text
            )


        answer = result.get(
            "answer"
        )

        if answer:

            return str(
                answer
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
    message: str,
) -> Optional[str]:

    """
    Compatibility function.

    Ollama is not part of the current
    Mistral-only routing.
    """

    ollama_url = os.getenv(
        "OLLAMA_URL",
        ""
    ).strip()


    if not ollama_url:

        return None


    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.1:8b"
    )


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
# PROVIDER STATUS
# ============================================================

def provider_status():

    return {

        "mistral":
            bool(
                MISTRAL_API_KEY
            ),

        "text": [
            "mistral"
        ],

        "vision": [
            "mistral"
        ],

        "image": [],

        "image_generation":
            False,

        "image_editing":
            False,
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
print("CURRENT PROVIDER: MISTRAL ONLY")
print("=" * 70)