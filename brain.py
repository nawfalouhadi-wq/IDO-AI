# ============================================================
# IDO AI - BRAIN.PY
# ============================================================
#
# FINAL PROVIDER ROUTING
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

# ------------------------------------------------------------
# MISTRAL TEXT
# ------------------------------------------------------------

MISTRAL_TEXT_MODEL = os.getenv(
    "MISTRAL_TEXT_MODEL",
    "mistral-medium-latest"
).strip()


# ------------------------------------------------------------
# GEMINI TEXT
# ------------------------------------------------------------

GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.6-flash"
).strip()


# ------------------------------------------------------------
# GEMINI IMAGE
# ------------------------------------------------------------

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
).strip()


# ------------------------------------------------------------
# GEMINI IMAGE EDIT
# ------------------------------------------------------------

GEMINI_IMAGE_EDIT_MODEL = os.getenv(
    "GEMINI_IMAGE_EDIT_MODEL",
    "gemini-3.1-flash-image"
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

print(
    "FINAL PROVIDER ROUTING"
)

print()

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
""")

print("""
IMAGE UNDERSTANDING:
    GEMINI ONLY
""")

print("""
IMAGE GENERATION:
    GEMINI ONLY
""")

print("""
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
        or AI_REQUEST_TIMEOUT
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
    # OpenAI-compatible
    # --------------------------------------------------------

    choices = data.get(
        "choices"
    )

    if (
        isinstance(
            choices,
            list
        )
        and choices
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
    # Gemini legacy generateContent
    # --------------------------------------------------------

    candidates = data.get(
        "candidates"
    )

    if (
        isinstance(
            candidates,
            list
        )
        and candidates
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


    # --------------------------------------------------------
    # output_text
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
# IMAGE EXTRACTION
# ============================================================

def _extract_image_data(
    data: Any
) -> Optional[str]:

    if not isinstance(
        data,
        dict
    ):

        return None


    # --------------------------------------------------------
    # Direct output_image
    # --------------------------------------------------------

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

            mime_type = output_image.get(
                "mime_type",
                "image/jpeg"
            )

            return (
                f"data:{mime_type};base64,"
                f"{image_data}"
            )


    # --------------------------------------------------------
    # Interaction steps
    # --------------------------------------------------------

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

                if item.get(
                    "type"
                ) != "image":

                    continue

                image_data = item.get(
                    "data"
                )

                if isinstance(
                    image_data,
                    str
                ) and image_data:

                    mime_type = item.get(
                        "mime_type",
                        "image/jpeg"
                    )

                    return (
                        f"data:{mime_type};base64,"
                        f"{image_data}"
                    )


    # --------------------------------------------------------
    # Standard data array
    # --------------------------------------------------------

    items = data.get(
        "data"
    )

    if isinstance(
        items,
        list
    ):

        for item in items:

            if not isinstance(
                item,
                dict
            ):

                continue

            b64 = item.get(
                "b64_json"
            )

            if isinstance(
                b64,
                str
            ) and b64:

                return (
                    "data:image/jpeg;base64,"
                    + b64
                )

            url = item.get(
                "url"
            )

            if isinstance(
                url,
                str
            ) and url:

                return url


    # --------------------------------------------------------
    # Recursive fallback
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

            if obj.startswith(
                "data:image/"
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

                if isinstance(
                    value,
                    str
                ):

                    if (
                        value.startswith(
                            "https://"
                        )
                        or
                        value.startswith(
                            "data:image/"
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
# IMAGE BYTES -> BASE64
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
                "role":
                    "system",

                "content":
                    (
                        "You are IDO AI. "
                        "Answer naturally and accurately. "
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

        "max_tokens":
            4096,
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
                        else (
                            MISTRAL_RETRY_BASE_SECONDS
                            * (
                                2 ** attempt
                            )
                        )
                    )

                except Exception:

                    delay = (
                        MISTRAL_RETRY_BASE_SECONDS
                        * (
                            2 ** attempt
                        )
                    )


                delay = min(
                    delay,
                    30
                )


                print(
                    "MISTRAL RATE LIMIT - "
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


            return None


    except Exception as exc:

        print(
            "MISTRAL TEXT EXCEPTION:",
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
        "GEMINI TEXT:"
        " COMPATIBILITY ONLY"
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
                "GEMINI TEXT ERROR:",
                response.status_code,
                response.text[:1000],
            )

            return None


        return (
            _extract_text(
                _safe_json(
                    response
                )
            )
            or None
        )


    except Exception as exc:

        print(
            "GEMINI TEXT EXCEPTION:",
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

        print(
            "GEMINI IMAGE: DISABLED"
        )

        return None


    print("=" * 70)

    print(
        "GEMINI IMAGE REQUEST"
    )

    print(
        "MODEL:",
        GEMINI_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        prompt
    )

    print(
        "OUTPUT MIME TYPE:",
        "image/jpeg"
    )

    print("=" * 70)


    url = (
        f"{GEMINI_BASE_URL}/interactions"
    )


    # IMPORTANT:
    #
    # Gemini 3.1 Flash Image currently expects
    # image/jpeg for response_format.mime_type.
    #
    # This fixes the exact 400 error from the log.


    payload = {

        "model":
            GEMINI_IMAGE_MODEL,

        "input":
            prompt,

        "response_format": {

            "type":
                "image",

            "mime_type":
                "image/jpeg",

            "aspect_ratio":
                "1:1",

            "image_size":
                "1K",
        },
    }


    try:

        response = requests.post(

            url,

            headers={

                "x-goog-api-key":
                    GEMINI_API_KEY,

                "Content-Type":
                    "application/json",
            },

            json=payload,

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


        image = _extract_image_data(
            data
        )


        if image:

            print(
                "GEMINI IMAGE SUCCESS"
            )

            return image


        print(
            "GEMINI IMAGE ERROR:",
            "No image data returned"
        )

        print(
            "GEMINI RESPONSE:",
            str(data)[:3000]
        )


    except Exception as exc:

        print(
            "GEMINI IMAGE EXCEPTION:",
            repr(exc)
        )


    return None


# ============================================================
# GEMINI IMAGE EDIT
# ============================================================

def _gemini_image_edit(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print("=" * 70)

    print(
        "GEMINI IMAGE EDIT REQUEST"
    )

    print(
        "MODEL:",
        GEMINI_IMAGE_EDIT_MODEL
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 70)


    # --------------------------------------------------------
    # Gemini image input
    #
    # Normalize the input MIME type to JPEG.
    #
    # This avoids sending image/png to an endpoint that
    # rejected it in the previous request.
    # --------------------------------------------------------

    input_mime = (
        mime_type
        or
        "image/jpeg"
    )


    # The current error specifically concerned output
    # response_format.mime_type. For maximum compatibility,
    # output is also requested as JPEG.


    encoded_image = _image_to_base64(
        image_bytes
    )


    url = (
        f"{GEMINI_BASE_URL}/interactions"
    )


    payload = {

        "model":
            GEMINI_IMAGE_EDIT_MODEL,

        "input": [

            {
                "type":
                    "text",

                "text":
                    prompt,
            },

            {
                "type":
                    "image",

                "mime_type":
                    input_mime,

                "data":
                    encoded_image,
            },
        ],

        "response_format": {

            "type":
                "image",

            "mime_type":
                "image/jpeg",

            "aspect_ratio":
                "1:1",

            "image_size":
                "1K",
        },
    }


    try:

        response = requests.post(

            url,

            headers={

                "x-goog-api-key":
                    GEMINI_API_KEY,

                "Content-Type":
                    "application/json",
            },

            json=payload,

            timeout=
                AI_REQUEST_TIMEOUT,
        )


        if response.status_code >= 400:

            print(
                "GEMINI IMAGE EDIT ERROR:",
                response.status_code,
                response.text[:2000],
            )

            return None


        data = _safe_json(
            response
        )


        image = _extract_image_data(
            data
        )


        if image:

            print(
                "GEMINI IMAGE EDIT SUCCESS"
            )

            return image


        print(
            "GEMINI IMAGE EDIT ERROR:",
            "No image returned"
        )


    except Exception as exc:

        print(
            "GEMINI IMAGE EDIT EXCEPTION:",
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
        message
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


# ============================================================
# IMAGE EDIT DETECTOR
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
        "IMAGE PROVIDER: GEMINI ONLY"
    )

    print(
        "PROMPT:",
        prompt
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
    mime_type: str = "image/jpeg",
) -> Optional[str]:

    print("=" * 70)

    print(
        "IMAGE EDITING START"
    )

    print(
        "IMAGE EDIT PROVIDER: GEMINI ONLY"
    )

    print("=" * 70)


    result = _gemini_image_edit(

        prompt,

        image_bytes,

        mime_type,
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

    print(
        "IMAGE PROVIDER: GEMINI ONLY"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # IMAGE EDIT
    # --------------------------------------------------------

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
            "image/jpeg",
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


    # --------------------------------------------------------
    # IMAGE GENERATION
    # --------------------------------------------------------

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


# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================

def _gemini_vision(
    message: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> Optional[str]:

    if not GEMINI_API_KEY:

        return None


    print("=" * 70)

    print(
        "GEMINI IMAGE UNDERSTANDING"
    )

    print(
        "MODEL:",
        GEMINI_IMAGE_MODEL
    )

    print(
        "PROMPT:",
        message
    )

    print("=" * 70)


    encoded_image = _image_to_base64(
        image_bytes
    )


    # --------------------------------------------------------
    # Use JPEG for the image input.
    #
    # If the browser uploaded PNG, the API may accept PNG
    # as input, but the current failing request showed that
    # this deployment expects JPEG in its image configuration.
    # --------------------------------------------------------

    input_mime = (
        mime_type
        or
        "image/jpeg"
    )


    url = (
        f"{GEMINI_BASE_URL}/interactions"
    )


    payload = {

        "model":
            GEMINI_IMAGE_MODEL,

        "input": [

            {
                "type":
                    "text",

                "text":
                    message,
            },

            {
                "type":
                    "image",

                "mime_type":
                    input_mime,

                "data":
                    encoded_image,
            },
        ],
    }


    try:

        response = requests.post(

            url,

            headers={

                "x-goog-api-key":
                    GEMINI_API_KEY,

                "Content-Type":
                    "application/json",
            },

            json=payload,

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


        return None


    except Exception as exc:

        print(
            "GEMINI VISION EXCEPTION:",
            repr(exc)
        )

        return None


# ============================================================
# IMAGE UNDERSTANDING
# ============================================================

def analyze_image(
    message: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> Optional[str]:

    print("=" * 70)

    print(
        "IMAGE UNDERSTANDING START"
    )

    print(
        "VISION PROVIDER: GEMINI ONLY"
    )

    print("=" * 70)


    result = _gemini_vision(

        message,

        image_bytes,

        mime_type,
    )


    if result:

        print(
            "VISION PROVIDER: GEMINI"
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
    # TEXT PROVIDER
    # --------------------------------------------------------

    result = _mistral_text(
        message
    )


    if result:

        print("=" * 70)

        print(
            "API CHAT SUCCESS"
        )

        print(
            "TEXT PROVIDER: MISTRAL"
        )

        print("=" * 70)

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


    # --------------------------------------------------------
    # No text fallback.
    #
    # User requested Mistral only.
    # --------------------------------------------------------

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

    Ollama is not part of the final routing.
    """

    return None


# ============================================================
# HEALTH / STATUS
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

            "mistral",

        ],

        "vision": [

            "gemini",

        ],

        "image": [

            "gemini",

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

print(
    "IDO AI BRAIN READY"
)

print("=" * 70)

print(
    "API BLUEPRINT: REGISTERED"
)

print("=" * 70)