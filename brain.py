import os
import base64
import uuid
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

from memory import (
    add_conversation_message,
    build_conversation_context,
    learn,
)


# ============================================================
# Ido AI - BRAIN.PY
# Fast / Clean / Failover Architecture
#
# TEXT:
#     Groq -> OpenRouter -> Mistral
#
# VISION:
#     Groq -> Mistral -> OpenRouter
#
# IMAGE GENERATION:
#     OpenRouter -> Mistral Agent
#
# DISABLED:
#     Gemini
#     xAI / Grok
# ============================================================


load_dotenv()


# ============================================================
# GENERAL SETTINGS
# ============================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "5")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "30")),
)

IMAGE_TIMEOUT = (
    int(os.getenv("IMAGE_CONNECT_TIMEOUT", "10")),
    int(os.getenv("IMAGE_READ_TIMEOUT", "180")),
)

CONVERSATION_CONTEXT_LIMIT = int(
    os.getenv(
        "CONVERSATION_CONTEXT_LIMIT",
        "12",
    )
)


# ============================================================
# GENERATED IMAGES DIRECTORY
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
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)

GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct",
)


if GROQ_API_KEY:

    print("GROQ CLIENT: READY")
    print("GROQ MODEL:", GROQ_MODEL)
    print("GROQ VISION MODEL:", GROQ_VISION_MODEL)

else:

    print("GROQ_API_KEY: NOT FOUND")


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free",
)

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "openrouter/free",
)

# ضع موديل صور حقيقي هنا في .env
OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "",
)


if OPENROUTER_API_KEY:

    print("OPENROUTER CLIENT: READY")
    print(
        "OPENROUTER MODEL:",
        OPENROUTER_MODEL,
    )

    print(
        "OPENROUTER VISION MODEL:",
        OPENROUTER_VISION_MODEL,
    )

    if OPENROUTER_IMAGE_MODEL:

        print(
            "OPENROUTER IMAGE MODEL:",
            OPENROUTER_IMAGE_MODEL,
        )

    else:

        print(
            "OPENROUTER IMAGE MODEL: NOT CONFIGURED"
        )

else:

    print(
        "OPENROUTER_API_KEY: NOT FOUND"
    )


# ============================================================
# MISTRAL
# ============================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "mistral-small-latest",
)

# اختياري - إذا أنشأت Mistral Image Agent
MISTRAL_IMAGE_AGENT_ID = os.getenv(
    "MISTRAL_IMAGE_AGENT_ID",
    "",
)


if MISTRAL_API_KEY:

    print("MISTRAL CLIENT: READY")
    print(
        "MISTRAL MODEL:",
        MISTRAL_MODEL,
    )

    print(
        "MISTRAL VISION MODEL:",
        MISTRAL_VISION_MODEL,
    )

    if MISTRAL_IMAGE_AGENT_ID:

        print(
            "MISTRAL IMAGE AGENT: READY"
        )

    else:

        print(
            "MISTRAL IMAGE AGENT: NOT CONFIGURED"
        )

else:

    print(
        "MISTRAL_API_KEY: NOT FOUND"
    )


# ============================================================
# DISABLED PROVIDERS
# ============================================================

print(
    "GEMINI: DISABLED"
)

print(
    "XAI / GROK: DISABLED"
)


# ============================================================
# STARTUP INFORMATION
# ============================================================

print(
    "================================================="
)

print(
    "IDO AI BRAIN.PY LOADED"
)

print(
    "TEXT ROUTE:"
    " GROQ -> OPENROUTER -> MISTRAL"
)

print(
    "VISION ROUTE:"
    " GROQ -> MISTRAL -> OPENROUTER"
)

print(
    "IMAGE ROUTE:"
    " OPENROUTER -> MISTRAL"
)

print(
    "IMAGE RESOLUTION:",
    IMAGE_RESOLUTION,
)

print(
    "================================================="
)


# ============================================================
# CLEAN ANSWER
# ============================================================

def clean_answer(answer):

    if answer is None:
        return None

    try:

        answer = str(answer).strip()

        if not answer:
            return None

        return answer

    except Exception:

        return None


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip().lower()

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


# ============================================================
# BUILT-IN RESPONSES
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

    "السلام عليكم ورحمه الله وبركاته":
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

    "من صممك":
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI.",

    "من صنع ido ai":
        "تم تطوير Ido AI وبناؤه "
        "بواسطة Noufal Ouhadi.",

    "من طور ido ai":
        "تم تطوير Ido AI بواسطة "
        "Noufal Ouhadi.",

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

    "وداعا":
        "إلى اللقاء! أتمنى لك يومًا سعيدًا.",
}


# ============================================================
# CONVERSATION CONTEXT
# ============================================================

def build_context_message(
    message,
    conversation_id=None,
    context_limit=CONVERSATION_CONTEXT_LIMIT,
):

    message = str(message or "").strip()

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
        "أنت Ido AI، مساعد ذكاء اصطناعي "
        "متعدد اللغات.\n\n"

        "أجب بطريقة طبيعية ومفيدة ومباشرة.\n"
        "يمكنك فهم العربية والدارجة المغربية "
        "والفرنسية والإنجليزية.\n\n"

        "لديك سياق المحادثة السابقة أدناه. "
        "استخدمه فقط عندما يكون مفيدًا للإجابة.\n\n"

        "## سياق المحادثة:\n"
        f"{context}\n\n"

        "## الرسالة الجديدة:\n"
        f"{message}\n\n"

        "لا تكرر سياق المحادثة للمستخدم."
    )


# ============================================================
# SAVE AI RESPONSE
# ============================================================

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
# EXTRACT CHAT CONTENT
# ============================================================

def extract_response_content(data):

    if not isinstance(data, dict):
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

            if not isinstance(
                item,
                dict,
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

            return clean_answer(
                "\n".join(parts)
            )

    return None


# ============================================================
# SAVE GENERATED IMAGE
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


# ============================================================
# EXTRACT BASE64 IMAGES
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

            if key_text in (
                "b64_json",
                "base64",
                "image_base64",
            ):

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


# ============================================================
# EXTRACT IMAGE URLS
# ============================================================

def extract_image_urls_deep(
    value,
    found=None,
    depth=0,
):

    if found is None:
        found = []

    if depth > 12:
        return found

    if value is None:
        return found

    if isinstance(
        value,
        str,
    ):

        urls = re.findall(
            r"https?://[^\s\"'<>]+",
            value,
        )

        for url in urls:

            url = url.rstrip(
                ".,);]"
            )

            if any(
                item in url.lower()
                for item in (
                    "image",
                    "images",
                    "generated",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                )
            ):

                found.append(
                    url
                )

        return found

    if isinstance(
        value,
        dict,
    ):

        for item in value.values():

            extract_image_urls_deep(
                item,
                found,
                depth + 1,
            )

        return found

    if isinstance(
        value,
        (list, tuple),
    ):

        for item in value:

            extract_image_urls_deep(
                item,
                found,
                depth + 1,
            )

    return found


# ============================================================
# FAST ERROR CHECK
# ============================================================

def is_permanent_provider_error(
    status_code,
):

    return status_code in (
        401,
        403,
        404,
        429,
    )


# ============================================================
# GROQ - TEXT
# ============================================================

def ask_groq(
    message,
):

    if not GROQ_API_KEY:
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
                    "application/json",
            },

            json={
                "model":
                    GROQ_MODEL,

                "messages": [
                    {
                        "role":
                            "system",

                        "content":
                            (
                                "You are Ido AI. "
                                "Be helpful, natural, "
                                "accurate and concise."
                            ),
                    },

                    {
                        "role":
                            "user",

                        "content":
                            message,
                    },
                ],

                "temperature":
                    0.7,

                "max_completion_tokens":
                    2048,
            },

            timeout=REQUEST_TIMEOUT,
        )

        print(
            "Groq Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Groq Response:",
                response.text[:2000],
            )

            return None

        answer = extract_response_content(
            response.json()
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

    except requests.exceptions.Timeout:

        print(
            "Groq ERROR: timeout."
        )

    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: connection failed."
        )

    except Exception as e:

        print(
            "Groq ERROR:",
            e,
        )

    return None


# ============================================================
# GROQ - VISION
# ============================================================

def ask_groq_image(
    message,
    image_bytes,
    mime_type,
):

    if not GROQ_API_KEY:
        return None

    if not image_bytes:
        return None

    try:

        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode(
                "utf-8"
            )
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        print(
            "Trying Groq Vision..."
        )

        response = requests.post(

            GROQ_URL,

            headers={
                "Authorization":
                    f"Bearer {GROQ_API_KEY}",

                "Content-Type":
                    "application/json",
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
                                    message,
                            },

                            {
                                "type":
                                    "image_url",

                                "image_url": {
                                    "url":
                                        image_data_url,
                                },
                            },

                        ],
                    },

                ],

                "temperature":
                    0.5,

                "max_completion_tokens":
                    2048,
            },

            timeout=REQUEST_TIMEOUT,
        )

        print(
            "Groq Vision Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Groq Vision Response:",
                response.text[:2000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "GROQ VISION ERROR:",
            e,
        )

        return None


# ============================================================
# OPENROUTER - TEXT
# ============================================================

def ask_openrouter(
    message,
):

    if not OPENROUTER_API_KEY:
        return None

    if not message:
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

                "HTTP-Referer":
                    "https://ido-ai-production.up.railway.app",

                "X-Title":
                    "Ido AI",
            },

            json={
                "model":
                    OPENROUTER_MODEL,

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            message,
                    },
                ],
            },

            timeout=REQUEST_TIMEOUT,
        )

        print(
            "OpenRouter Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenRouter Response:",
                response.text[:2000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "OPENROUTER ERROR:",
            e,
        )

        return None


# ============================================================
# OPENROUTER - VISION
# ============================================================

def ask_openrouter_image(
    message,
    image_bytes,
    mime_type,
):

    if not OPENROUTER_API_KEY:
        return None

    if not image_bytes:
        return None

    try:

        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode(
                "utf-8"
            )
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        print(
            "Trying OpenRouter Vision..."
        )

        response = requests.post(

            OPENROUTER_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "HTTP-Referer":
                    "https://ido-ai-production.up.railway.app",

                "X-Title":
                    "Ido AI",
            },

            json={
                "model":
                    OPENROUTER_VISION_MODEL,

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
                                        image_data_url,
                                },
                            },

                        ],
                    },

                ],
            },

            timeout=REQUEST_TIMEOUT,
        )

        print(
            "OpenRouter Vision Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenRouter Vision Response:",
                response.text[:2000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "OPENROUTER VISION ERROR:",
            e,
        )

        return None


# ============================================================
# OPENROUTER - IMAGE GENERATION
# ============================================================

def generate_image_with_openrouter(
    prompt,
):

    if not OPENROUTER_API_KEY:

        print(
            "OPENROUTER IMAGE: "
            "API KEY NOT FOUND"
        )

        return None

    if not OPENROUTER_IMAGE_MODEL:

        print(
            "OPENROUTER IMAGE MODEL: "
            "NOT CONFIGURED"
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
            OPENROUTER_IMAGE_MODEL,
        )

        response = requests.post(

            OPENROUTER_IMAGE_URL,

            headers={
                "Authorization":
                    f"Bearer {OPENROUTER_API_KEY}",

                "Content-Type":
                    "application/json",

                "HTTP-Referer":
                    "https://ido-ai-production.up.railway.app",

                "X-Title":
                    "Ido AI",
            },

            json={
                "model":
                    OPENROUTER_IMAGE_MODEL,

                "prompt":
                    prompt,

                "resolution":
                    IMAGE_RESOLUTION,
            },

            timeout=IMAGE_TIMEOUT,
        )

        print(
            "OpenRouter Image Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "OpenRouter Image Response:",
                response.text[:3000],
            )

            return None

        data = response.json()

        images = extract_base64_images(
            data
        )

        for encoded_image in images:

            try:

                if "," in encoded_image:

                    encoded_image = (
                        encoded_image.split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = (
                    base64.b64decode(
                        encoded_image
                    )
                )

                image_url = (
                    save_generated_image(
                        image_bytes
                    )
                )

                if image_url:

                    print(
                        "OPENROUTER IMAGE SAVED:",
                        image_url,
                    )

                    return image_url

            except Exception as e:

                print(
                    "OPENROUTER BASE64 ERROR:",
                    e,
                )

        print(
            "OPENROUTER IMAGE: "
            "No image data returned."
        )

    except requests.exceptions.Timeout:

        print(
            "OPENROUTER IMAGE ERROR: timeout."
        )

    except Exception as e:

        print(
            "OPENROUTER IMAGE ERROR:",
            e,
        )

    return None


# ============================================================
# MISTRAL - TEXT
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
                    },
                ],

                "temperature":
                    0.7,

                "max_tokens":
                    2048,
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
                response.text[:2000],
            )

            return None

        answer = extract_response_content(
            response.json()
        )

        if answer:

            print(
                "Mistral response received."
            )

            return answer

    except Exception as e:

        print(
            "MISTRAL ERROR:",
            e,
        )

    return None


# ============================================================
# MISTRAL - VISION
# ============================================================

def ask_mistral_image(
    message,
    image_bytes,
    mime_type,
):

    if not MISTRAL_API_KEY:
        return None

    if not image_bytes:
        return None

    try:

        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode(
                "utf-8"
            )
        )

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        print(
            "Trying Mistral Vision..."
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
                                        image_data_url,
                                },
                            },

                        ],
                    },

                ],

                "temperature":
                    0.5,

                "max_tokens":
                    2048,
            },

            timeout=REQUEST_TIMEOUT,
        )

        print(
            "Mistral Vision Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Mistral Vision Response:",
                response.text[:2000],
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "MISTRAL VISION ERROR:",
            e,
        )

        return None


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(
    prompt,
):

    if not prompt:
        return None

    prompt = str(
        prompt
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
    # 1. OpenRouter
    # --------------------------------------------------------

    generated = (
        generate_image_with_openrouter(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: "
            "OPENROUTER"
        )

        return generated

    print(
        "OpenRouter image generation failed."
    )

    # --------------------------------------------------------
    # 2. Mistral Agent
    # --------------------------------------------------------

    generated = (
        generate_image_with_mistral_agent(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: "
            "MISTRAL"
        )

        return generated

    print(
        "Mistral image generation failed."
    )

    print(
        "IMAGE GENERATION FAILED."
    )

    return None


# ============================================================
# MISTRAL IMAGE AGENT
# ============================================================

def generate_image_with_mistral_agent(
    prompt,
):

    if not MISTRAL_API_KEY:
        return None

    if not MISTRAL_IMAGE_AGENT_ID:

        print(
            "MISTRAL IMAGE AGENT: "
            "NOT CONFIGURED"
        )

        return None

    try:

        print(
            "MISTRAL IMAGE AGENT STARTED"
        )

        # يتم استخدام API الخاصة بالمحادثات
        # مع Agent تم تفعيل image_generation له.

        url = (
            "https://api.mistral.ai/v1/"
            "conversations"
        )

        response = requests.post(

            url,

            headers={
                "Authorization":
                    f"Bearer {MISTRAL_API_KEY}",

                "Content-Type":
                    "application/json",
            },

            json={
                "agent_id":
                    MISTRAL_IMAGE_AGENT_ID,

                "inputs":
                    prompt,
            },

            timeout=IMAGE_TIMEOUT,
        )

        print(
            "Mistral Image Agent Status:",
            response.status_code,
        )

        if response.status_code != 200:

            print(
                "Mistral Image Agent Response:",
                response.text[:3000],
            )

            return None

        data = response.json()

        # محاولة العثور على file_id
        # الناتج من Image Generation Tool.

        file_ids = []

        def scan(
            value,
            depth=0,
        ):

            if depth > 15:
                return

            if isinstance(
                value,
                dict,
            ):

                for key, item in value.items():

                    key_lower = str(
                        key
                    ).lower()

                    if (
                        key_lower == "file_id"
                        and isinstance(
                            item,
                            str,
                        )
                    ):

                        file_ids.append(
                            item
                        )

                    scan(
                        item,
                        depth + 1,
                    )

            elif isinstance(
                value,
                list,
            ):

                for item in value:

                    scan(
                        item,
                        depth + 1,
                    )

        scan(data)

        file_ids = list(
            dict.fromkeys(
                file_ids
            )
        )

        if not file_ids:

            print(
                "MISTRAL IMAGE AGENT: "
                "NO FILE ID FOUND"
            )

            return None

        for file_id in file_ids:

            try:

                download_url = (
                    "https://api.mistral.ai/v1/"
                    f"files/{file_id}/content"
                )

                image_response = (
                    requests.get(
                        download_url,

                        headers={
                            "Authorization":
                                f"Bearer "
                                f"{MISTRAL_API_KEY}",
                        },

                        timeout=IMAGE_TIMEOUT,
                    )
                )

                if (
                    image_response.status_code
                    != 200
                ):

                    continue

                image_url = (
                    save_generated_image(
                        image_response.content
                    )
                )

                if image_url:

                    print(
                        "MISTRAL IMAGE SAVED:",
                        image_url,
                    )

                    return image_url

            except Exception as e:

                print(
                    "MISTRAL IMAGE DOWNLOAD ERROR:",
                    e,
                )

    except Exception as e:

        print(
            "MISTRAL IMAGE AGENT ERROR:",
            e,
        )

    return None


# ============================================================
# IMAGE GENERATION INTENT
# ============================================================

def is_image_generation_request(
    message,
):

    text = normalize_text(
        message
    )

    if not text:
        return False

    direct_phrases = [

        "ولد لي صورة",
        "ولد صورة",
        "انشئ لي صورة",
        "انشئ صورة",
        "اصنع لي صورة",
        "اصنع صورة",
        "ارسم لي صورة",
        "ارسم صورة",
        "صمم لي صورة",
        "صمم صورة",
        "اعمل لي صورة",
        "اعمل صورة",
        "توليد صورة",
        "توليد لي صورة",

        "اريد صورة",
        "اريد صوره",
        "اريدك تولد صورة",
        "اريدك تنشئ صورة",
        "اريدك تصنع صورة",

        "بغيتك تنشئ لي صورة",
        "بغيتك تصنع لي صورة",
        "بغيتك ترسم لي صورة",

        "واش تقدر تنشئ صورة",
        "واش تقدر تنشئ لي صورة",

        "ممكن تنشئ صورة",
        "ممكن تنشئ لي صورة",

        "generate an image",
        "generate image",
        "generate a picture",

        "create an image",
        "create image",
        "create a picture",

        "make an image",
        "make image",
        "make a picture",

        "draw an image",
        "draw image",
        "draw a picture",
    ]

    for phrase in direct_phrases:

        if normalize_text(
            phrase
        ) in text:

            print(
                "IMAGE GENERATION INTENT:",
                text,
            )

            return True

    has_image_word = any(
        word in text
        for word in (
            "صورة",
            "صوره",
            "image",
            "picture",
            "artwork",
        )
    )

    has_generation_word = any(
        word in text
        for word in (
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
    )

    return (
        has_image_word
        and has_generation_word
    )


# ============================================================
# IMAGE PROMPT
# ============================================================

def get_image_prompt(
    message,
):

    if not message:
        return ""

    text = str(
        message
    ).strip()

    # حذف التحيات
    text = re.sub(
        r"^(السلام عليكم ورحمة الله وبركاته|"
        r"السلام عليكم|مرحبا|مرحباً|اهلا|أهلا)"
        r"[،,\s]*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # حذف عبارات الطلب
    prefixes = [

        "هل يمكنك",
        "هل تقدر",
        "هل تستطيع",
        "واش تقدر",
        "واش ممكن",
        "ممكن",
        "تقدر",
        "تستطيع",
        "بغيتك",
        "اريدك",
        "أريدك",
        "ابغى",
    ]

    changed = True

    while changed:

        changed = False

        normalized = normalize_text(
            text
        )

        for prefix in prefixes:

            p = normalize_text(
                prefix
            )

            if normalized.startswith(
                p + " "
            ):

                text = text[
                    len(prefix):
                ].strip()

                changed = True
                break

    # حذف أفعال التوليد
    actions = [

        "ولد لي",
        "ولد",
        "انشئ لي",
        "انشئ",
        "أنشئ لي",
        "أنشئ",
        "اصنع لي",
        "اصنع",
        "ارسم لي",
        "ارسم",
        "صمم لي",
        "صمم",
        "اعمل لي",
        "اعمل",
        "توليد لي",
        "توليد",
        "تنشئ لي",
        "تنشئ",
        "generate",
        "create",
        "make",
        "draw",
    ]

    changed = True

    while changed:

        changed = False

        normalized = normalize_text(
            text
        )

        for action in actions:

            a = normalize_text(
                action
            )

            if normalized.startswith(
                a + " "
            ):

                text = text[
                    len(action):
                ].strip()

                changed = True
                break

    # حذف كلمة صورة إذا كانت في البداية
    image_words = [
        "صورة",
        "صوره",
        "image",
        "picture",
    ]

    normalized = normalize_text(
        text
    )

    for word in image_words:

        w = normalize_text(
            word
        )

        if normalized.startswith(
            w + " "
        ):

            text = text[
                len(word):
            ].strip()

            break

    text = text.strip(
        " \t\n\r.,،:؛!?؟"
    )

    if not text:

        return (
            "A beautiful high-quality "
            "photorealistic image, "
            "cinematic lighting, realistic "
            "details, professional composition, "
            "high resolution."
        )

    return text


# ============================================================
# IMAGE EDIT INTENT
# ============================================================

def is_image_edit_request(
    message,
):

    text = normalize_text(
        message
    )

    if not text:
        return False

    edit_words = [

        "اجعل",
        "خلي",
        "بدل",
        "استبدل",
        "غير",
        "تغيير",
        "عدل",
        "تعديل",
        "حول",

        "edit",
        "modify",
        "change",
        "replace",
        "transform",
        "make it",
        "turn it into",
    ]

    return any(
        normalize_text(word)
        in text
        for word in edit_words
    )


# ============================================================
# IMAGE EDIT PROMPT
# ============================================================

def build_image_edit_prompt(
    image_description,
    edit_request,
):

    description = (
        image_description
        or
        "A realistic scene containing "
        "the main subject shown in "
        "the original image."
    )

    request = (
        edit_request
        or
        "Keep the scene unchanged."
    )

    return (
        "Create a photorealistic image "
        "based on the following source scene.\n\n"

        "SOURCE SCENE:\n"
        f"{description}\n\n"

        "REQUESTED EDIT:\n"
        f"{request}\n\n"

        "IMPORTANT:\n"
        "- Preserve the original composition.\n"
        "- Preserve the camera viewpoint.\n"
        "- Preserve the environment.\n"
        "- Preserve the main subject's position.\n"
        "- Preserve lighting unless requested otherwise.\n"
        "- Change only what the user requested.\n"
        "- Do not add unrelated objects.\n"
        "- Keep everything visually coherent.\n"
        "- Produce a realistic high-quality image."
    )


# ============================================================
# IMAGE EDIT
# ============================================================

def edit_image(
    edit_request,
    image_bytes,
    mime_type,
):

    if not edit_request:
        return None

    if not image_bytes:
        return None

    print(
        "IMAGE EDIT REQUEST:",
        edit_request,
    )

    analysis_prompt = (
        "Describe this image in detailed "
        "visual terms. Focus on composition, "
        "camera angle, subject, colors, "
        "environment, background, lighting, "
        "shadows and spatial relationships. "
        "Return only the visual description."
    )

    # --------------------------------------------------------
    # Analyze source image
    # --------------------------------------------------------

    image_description = (
        ask_groq_image(
            analysis_prompt,
            image_bytes,
            mime_type,
        )
    )

    if not image_description:

        image_description = (
            ask_mistral_image(
                analysis_prompt,
                image_bytes,
                mime_type,
            )
        )

    if not image_description:

        image_description = (
            ask_openrouter_image(
                analysis_prompt,
                image_bytes,
                mime_type,
            )
        )

    if not image_description:

        print(
            "IMAGE EDIT ERROR: "
            "SOURCE IMAGE ANALYSIS FAILED"
        )

        return None

    edit_prompt = (
        build_image_edit_prompt(
            image_description,
            edit_request,
        )
    )

    print(
        "FINAL IMAGE EDIT PROMPT:",
        edit_prompt,
    )

    return generate_image(
        edit_prompt
    )


# ============================================================
# MAIN RESPONSE
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
    # IMAGE GENERATION
    # ========================================================

    if is_image_generation_request(
        original_message
    ):

        print(
            "DIRECT IMAGE GENERATION REQUEST:",
            original_message,
        )

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
                    "تم إنشاء الصورة بناءً على طلبك.",
                    conversation_id,
                    source="image_generation",
                )

            return (
                "IMAGE_URL:"
                + generated
            )

        return (
            "تعذر إنشاء الصورة حاليًا. "
            "تأكد من إعداد OPENROUTER_IMAGE_MODEL "
            "أو MISTRAL_IMAGE_AGENT_ID."
        )

    # ========================================================
    # BUILT-IN RESPONSES
    # ========================================================

    normalized_message = normalize_text(
        original_message
    )

    builtin_answer = (
        BUILTIN_RESPONSES.get(
            normalized_message
        )
    )

    if builtin_answer:

        if (
            save_response
            and conversation_id
        ):

            save_ai_response(
                original_message,
                builtin_answer,
                conversation_id,
                source="builtin",
            )

        return builtin_answer

    # ========================================================
    # CONTEXT
    # ========================================================

    model_message = build_context_message(
        original_message,
        conversation_id,
    )

    # ========================================================
    # 1. GROQ
    # ========================================================

    answer = ask_groq(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="groq",
            )

        return answer

    # ========================================================
    # 2. OPENROUTER
    # ========================================================

    print(
        "Groq failed. "
        "Trying OpenRouter..."
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
    # 3. MISTRAL
    # ========================================================

    print(
        "OpenRouter failed. "
        "Trying Mistral..."
    )

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
    # ALL PROVIDERS FAILED
    # ========================================================

    fallback = (
        "أنا Ido AI ولم أجد إجابة حاليًا."
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
# IMAGE RESPONSE
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

    if (
        not message
        or not str(message).strip()
    ):

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    message = str(
        message
    ).strip()

    # ========================================================
    # IMAGE EDIT
    # ========================================================

    if is_image_edit_request(
        message
    ):

        generated_image = edit_image(
            message,
            image_bytes,
            mime_type,
        )

        if generated_image:

            if conversation_id:

                save_ai_response(
                    message,
                    "تم تعديل الصورة بناءً على طلبك.",
                    conversation_id,
                    source="image_edit",
                )

            return (
                "IMAGE_URL:"
                + generated_image
            )

        return (
            "تعذر تعديل الصورة حاليًا."
        )

    # ========================================================
    # GROQ VISION
    # ========================================================

    print(
        "VISION ROUTE: GROQ"
    )

    answer = ask_groq_image(
        message,
        image_bytes,
        mime_type,
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="groq_vision",
            )

        return answer

    # ========================================================
    # MISTRAL VISION
    # ========================================================

    print(
        "Groq Vision failed. "
        "Trying Mistral Vision..."
    )

    answer = ask_mistral_image(
        message,
        image_bytes,
        mime_type,
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="mistral_vision",
            )

        return answer

    # ========================================================
    # OPENROUTER VISION
    # ========================================================

    print(
        "Mistral Vision failed. "
        "Trying OpenRouter Vision..."
    )

    answer = ask_openrouter_image(
        message,
        image_bytes,
        mime_type,
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="openrouter_vision",
            )

        return answer

    # ========================================================
    # FAILED
    # ========================================================

    fallback = (
        "تعذر تحليل الصورة حاليًا."
    )

    if conversation_id:

        save_ai_response(
            message,
            fallback,
            conversation_id,
            source="image_fallback",
        )

    return fallback