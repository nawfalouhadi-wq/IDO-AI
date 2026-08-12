import os
import base64
import uuid
import re
from pathlib import Path

import requests

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

from memory import (
    add_conversation_message,
    build_conversation_context,
    learn
)

# =========================================================
# تحميل .env
# =========================================================

load_dotenv()

# =========================================================
# إعدادات عامة
# =========================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "5")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "30"))
)

OPENROUTER_TIMEOUT = (
    int(os.getenv("OPENROUTER_CONNECT_TIMEOUT", "5")),
    int(os.getenv("OPENROUTER_READ_TIMEOUT", "60"))
)

IMAGE_TIMEOUT = (
    int(os.getenv("IMAGE_CONNECT_TIMEOUT", "10")),
    int(os.getenv("IMAGE_READ_TIMEOUT", "180"))
)

CONVERSATION_CONTEXT_LIMIT = int(
    os.getenv(
        "CONVERSATION_CONTEXT_LIMIT",
        "12"
    )
)

# =========================================================
# مجلد الصور الناتجة
# =========================================================

GENERATED_IMAGE_DIR = Path(
    os.getenv(
        "GENERATED_IMAGE_DIR",
        "static/generated"
    )
)

try:
    GENERATED_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
except Exception as e:
    print(
        "GENERATED IMAGE DIRECTORY ERROR:",
        e
    )

# =========================================================
# إعدادات الصور
# =========================================================

IMAGE_RESOLUTION = os.getenv(
    "IMAGE_RESOLUTION",
    "2K"
).upper()

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3-pro-image-preview"
)

GROQ_IMAGE_MODEL = os.getenv(
    "GROQ_IMAGE_MODEL",
    ""
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    ""
)

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    ""
)

# =========================================================
# Gemini
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

GEMINI_TIMEOUT_MS = 30000

gemini_client = None

if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=GEMINI_TIMEOUT_MS
            )
        )

        print("GEMINI CLIENT: READY")
        print(
            "GEMINI MODEL:",
            GEMINI_MODEL
        )
        print(
            "GEMINI IMAGE MODEL:",
            GEMINI_IMAGE_MODEL
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
# OpenRouter
# =========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_IMAGE_URL = (
    "https://openrouter.ai/api/v1/images"
)

if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
    )

    print(
        "OPENROUTER TIMEOUT:",
        OPENROUTER_TIMEOUT
    )

    if OPENROUTER_IMAGE_MODEL:

        print(
            "OPENROUTER IMAGE MODEL:",
            OPENROUTER_IMAGE_MODEL
        )

else:

    print(
        "OPENROUTER_API_KEY: NOT FOUND"
    )

# =========================================================
# Groq
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

    print(
        "GROQ CLIENT: READY"
    )

    print(
        "GROQ MODEL:",
        GROQ_MODEL
    )

    print(
        "GROQ VISION MODEL:",
        GROQ_VISION_MODEL
    )

    if GROQ_IMAGE_MODEL:

        print(
            "GROQ IMAGE MODEL:",
            GROQ_IMAGE_MODEL
        )

else:

    print(
        "GROQ_API_KEY: NOT FOUND"
    )

# =========================================================
# Mistral
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
# معلومات التشغيل
# =========================================================

print(
    "================================================="
)

print(
    "BRAIN.PY LOADED"
)

print(
    "TEXT ROUTE:"
    " GEMINI -> GROQ -> OPENROUTER -> MISTRAL"
)

print(
    "IMAGE ROUTE:"
    " GEMINI -> GROQ -> OPENROUTER -> MISTRAL"
)

print(
    "IMAGE RESOLUTION:",
    IMAGE_RESOLUTION
)

print(
    "================================================="
)

# =========================================================
# تنظيف الإجابة
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
# تطبيع النص
# =========================================================

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
        "ئ": "ي"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
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
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# =========================================================
# الردود الثابتة
# =========================================================

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

    "السلام عليكم ورحمة الله وبركاته":
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

    "من انشاك":
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
        "إلى اللقاء! أتمنى لك يومًا سعيدًا."
}


# =========================================================
# سياق المحادثة
# =========================================================

def build_context_message(
    message,
    conversation_id=None,
    context_limit=CONVERSATION_CONTEXT_LIMIT
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
            context_limit
        )

    except Exception as e:

        print(
            "CONVERSATION CONTEXT ERROR:",
            e
        )

        context = ""

    if not context:
        return message

    return (
        "أنت Aido AI، مساعد ذكاء اصطناعي.\n\n"
        "لديك سياق المحادثة السابقة أدناه.\n"
        "استخدمه لفهم الأسئلة المختصرة والأسئلة "
        "التي تعتمد على الرسائل السابقة.\n\n"
        "## سياق المحادثة:\n\n"
        f"{context}\n\n"
        "## الرسالة الجديدة:\n\n"
        f"{message}\n\n"
        "أجب عن الرسالة الجديدة اعتمادًا على "
        "السياق عندما يكون ذلك مفيدًا.\n"
        "لا تكرر سياق المحادثة كاملًا للمستخدم."
    )


# =========================================================
# حفظ الإجابة
# =========================================================

def save_ai_response(
    question,
    answer,
    conversation_id=None,
    source="ai"
):

    if not question or not answer:
        return

    try:

        learn(
            question,
            answer,
            source=source
        )

    except Exception as e:

        print(
            "MEMORY LEARN ERROR:",
            e
        )

    if conversation_id:

        try:

            add_conversation_message(
                question,
                answer,
                conversation_id=conversation_id
            )

        except Exception as e:

            print(
                "CONVERSATION SAVE ERROR:",
                e
            )


# =========================================================
# استخراج محتوى Chat Completions
# =========================================================

def extract_response_content(data):

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

    if not isinstance(
        message_data,
        dict
    ):

        return None

    content = message_data.get(
        "content"
    )

    if isinstance(
        content,
        str
    ):

        return clean_answer(
            content
        )

    if isinstance(
        content,
        list
    ):

        parts = []

        for item in content:

            if isinstance(
                item,
                dict
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


# =========================================================
# حفظ الصورة
# =========================================================

def save_generated_image(
    image_bytes
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
            e
        )

        return None


# =========================================================
# استخراج Base64 من استجابة الصور
# =========================================================

def extract_base64_images(
    data
):

    found = []

    if data is None:
        return found

    if isinstance(
        data,
        dict
    ):

        for key, value in data.items():

            key_text = str(
                key
            ).lower()

            if key_text in (
                "b64_json",
                "base64",
                "image_base64"
            ):

                if isinstance(
                    value,
                    str
                ) and value.strip():

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
        list
    ):

        for item in data:

            found.extend(
                extract_base64_images(
                    item
                )
            )

        return found

    return found


# =========================================================
# استخراج URL للصور
# =========================================================

def extract_image_urls_deep(
    value,
    found=None,
    depth=0
):

    if found is None:
        found = []

    if depth > 12:
        return found

    if value is None:
        return found

    if isinstance(
        value,
        str
    ):

        urls = re.findall(
            r"https?://[^\s\"'<>]+",
            value
        )

        for url in urls:

            clean_url = url.rstrip(
                ".,);]"
            )

            if any(
                item in clean_url.lower()
                for item in (
                    "image",
                    "images",
                    "generated",
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                )
            ):

                found.append(
                    clean_url
                )

        return found

    if isinstance(
        value,
        dict
    ):

        for item in value.values():

            extract_image_urls_deep(
                item,
                found,
                depth + 1
            )

        return found

    if isinstance(
        value,
        (list, tuple)
    ):

        for item in value:

            extract_image_urls_deep(
                item,
                found,
                depth + 1
            )

        return found

    for attribute in (
        "content",
        "outputs",
        "choices",
        "message",
        "messages",
        "output",
        "url",
        "image_url"
    ):

        try:

            item = getattr(
                value,
                attribute,
                None
            )

        except Exception:

            item = None

        if item is not None:

            extract_image_urls_deep(
                item,
                found,
                depth + 1
            )

    return found


# =========================================================
# Gemini - نص
# =========================================================

def ask_gemini(
    message
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
            gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=message
            )
        )

        if not response:
            return None

        answer = clean_answer(
            getattr(
                response,
                "text",
                None
            )
        )

        if answer:

            print(
                "Gemini response received."
            )

            return answer

        return None

    except Exception as e:

        print(
            "Gemini ERROR:",
            e
        )

        return None


# =========================================================
# Gemini - توليد الصور
# =========================================================

def generate_image_with_gemini(
    prompt
):

    if gemini_client is None:
        return None

    if not prompt:
        return None

    try:

        print(
            "===================================="
        )

        print(
            "GEMINI IMAGE GENERATION STARTED"
        )

        print(
            "GEMINI IMAGE MODEL:",
            GEMINI_IMAGE_MODEL
        )

        print(
            "GEMINI IMAGE RESOLUTION:",
            IMAGE_RESOLUTION
        )

        print(
            "GEMINI IMAGE PROMPT:",
            prompt
        )

        response = (
            gemini_client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=prompt,
                config={
                    "response_modalities": [
                        "TEXT",
                        "IMAGE"
                    ],
                    "image_config": {
                        "image_size":
                            IMAGE_RESOLUTION
                    }
                }
            )
        )

        if not response:
            return None

        candidates = getattr(
            response,
            "candidates",
            None
        )

        if not candidates:
            return None

        for candidate in candidates:

            content = getattr(
                candidate,
                "content",
                None
            )

            if not content:
                continue

            parts = getattr(
                content,
                "parts",
                None
            )

            if not parts:
                continue

            for part in parts:

                inline_data = getattr(
                    part,
                    "inline_data",
                    None
                )

                if not inline_data:
                    continue

                image_data = getattr(
                    inline_data,
                    "data",
                    None
                )

                if not image_data:
                    continue

                image_url = save_generated_image(
                    image_data
                )

                if image_url:

                    print(
                        "GEMINI IMAGE SAVED:",
                        image_url
                    )

                    return image_url

        print(
            "GEMINI IMAGE: "
            "No image data returned."
        )

        return None

    except Exception as e:

        print(
            "GEMINI IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# OpenRouter - نص
# =========================================================

def ask_openrouter(
    message
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

                "X-Title":
                    "Ido AI"
            },

            json={
                "model":
                    "openrouter/free",

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            message
                    }
                ]
            },

            timeout=OPENROUTER_TIMEOUT
        )

        print(
            "OpenRouter Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OpenRouter Response:",
                response.text[:2000]
            )

            return None

        answer = extract_response_content(
            response.json()
        )

        if answer:

            print(
                "OpenRouter response received."
            )

            return answer

        return None

    except requests.exceptions.Timeout:

        print(
            "OpenRouter ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "OpenRouter ERROR: connection failed."
        )

        return None

    except Exception as e:

        print(
            "OpenRouter ERROR:",
            e
        )

        return None


# =========================================================
# OpenRouter - توليد الصور
# =========================================================

def generate_image_with_openrouter(
    prompt
):

    if not OPENROUTER_API_KEY:
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
            OPENROUTER_IMAGE_MODEL
        )

        print(
            "OPENROUTER IMAGE RESOLUTION:",
            IMAGE_RESOLUTION
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

                "resolution":
                    IMAGE_RESOLUTION
            },

            timeout=IMAGE_TIMEOUT
        )

        print(
            "OPENROUTER IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "OPENROUTER IMAGE RESPONSE:",
                response.text[:3000]
            )

            return None

        data = response.json()

        # -------------------------------------------------
        # Base64
        # -------------------------------------------------

        base64_images = extract_base64_images(
            data
        )

        for encoded_image in base64_images:

            try:

                if "," in encoded_image:

                    encoded_image = (
                        encoded_image.split(
                            ",",
                            1
                        )[1]
                    )

                image_bytes = base64.b64decode(
                    encoded_image
                )

            except Exception:

                continue

            image_url = save_generated_image(
                image_bytes
            )

            if image_url:

                print(
                    "OPENROUTER IMAGE SAVED:",
                    image_url
                )

                return image_url

        # -------------------------------------------------
        # URL
        # -------------------------------------------------

        image_urls = extract_image_urls_deep(
            data
        )

        image_urls = list(
            dict.fromkeys(
                image_urls
            )
        )

        if image_urls:

            print(
                "OPENROUTER IMAGE URL:",
                image_urls[0]
            )

            return image_urls[0]

        print(
            "OPENROUTER IMAGE: "
            "No image returned."
        )

        print(
            "OPENROUTER IMAGE DATA:",
            str(data)[:5000]
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "OPENROUTER IMAGE ERROR: timeout."
        )

        return None

    except Exception as e:

        print(
            "OPENROUTER IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Groq - نص
# =========================================================

def ask_groq(
    message
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
                    1024
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq Response:",
                response.text[:2000]
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

        return None

    except requests.exceptions.Timeout:

        print(
            "Groq ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: connection failed."
        )

        return None

    except Exception as e:

        print(
            "Groq ERROR:",
            e
        )

        return None


# =========================================================
# Groq - تحليل صورة
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
                    0.7,

                "max_completion_tokens":
                    1024
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Groq Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Groq Image Response:",
                response.text[:2000]
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "Groq IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Groq - توليد الصور
# =========================================================

def generate_image_with_groq(
    prompt
):

    if not GROQ_API_KEY:
        return None

    if not GROQ_IMAGE_MODEL:

        print(
            "GROQ IMAGE MODEL: "
            "NOT CONFIGURED"
        )

        return None

    if not prompt:
        return None

    try:

        print(
            "GROQ IMAGE GENERATION STARTED"
        )

        print(
            "GROQ IMAGE MODEL:",
            GROQ_IMAGE_MODEL
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
                    GROQ_IMAGE_MODEL,

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            prompt
                    }
                ]
            },

            timeout=IMAGE_TIMEOUT
        )

        print(
            "GROQ IMAGE STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "GROQ IMAGE RESPONSE:",
                response.text[:3000]
            )

            return None

        data = response.json()

        # -------------------------------------------------
        # Base64
        # -------------------------------------------------

        base64_images = extract_base64_images(
            data
        )

        for encoded_image in base64_images:

            try:

                if "," in encoded_image:

                    encoded_image = (
                        encoded_image.split(
                            ",",
                            1
                        )[1]
                    )

                image_bytes = base64.b64decode(
                    encoded_image
                )

            except Exception:

                continue

            image_url = save_generated_image(
                image_bytes
            )

            if image_url:

                print(
                    "GROQ IMAGE SAVED:",
                    image_url
                )

                return image_url

        # -------------------------------------------------
        # URL
        # -------------------------------------------------

        image_urls = extract_image_urls_deep(
            data
        )

        image_urls = list(
            dict.fromkeys(
                image_urls
            )
        )

        if image_urls:

            return image_urls[0]

        print(
            "GROQ IMAGE: "
            "No image returned."
        )

        return None

    except Exception as e:

        print(
            "GROQ IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Mistral - نص
# =========================================================

def ask_mistral(
    message
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
                    1024
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral Response:",
                response.text[:2000]
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

        return None

    except requests.exceptions.Timeout:

        print(
            "Mistral ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Mistral ERROR: connection failed."
        )

        return None

    except Exception as e:

        print(
            "Mistral ERROR:",
            e
        )

        return None


# =========================================================
# Mistral - تحليل صورة
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
                    0.7,

                "max_tokens":
                    1024
            },

            timeout=REQUEST_TIMEOUT
        )

        print(
            "Mistral Image Status:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "Mistral Image Response:",
                response.text[:2000]
            )

            return None

        return extract_response_content(
            response.json()
        )

    except Exception as e:

        print(
            "MISTRAL IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Mistral - توليد الصور
# =========================================================

def generate_image_with_mistral(
    prompt
):

    if not MISTRAL_API_KEY:
        return None

    if not MISTRAL_IMAGE_MODEL:

        print(
            "MISTRAL IMAGE MODEL: "
            "NOT CONFIGURED"
        )

        return None

    print(
        "MISTRAL IMAGE GENERATION "
        "IS CONFIGURED AS LAST FALLBACK."
    )

    return None


# =========================================================
# مولد الصور الرئيسي
#
# Gemini
#   ↓
# Groq
#   ↓
# OpenRouter
#   ↓
# Mistral
# =========================================================

def generate_image(
    prompt
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
        prompt
    )

    # =====================================================
    # 1. Gemini - الأساسي
    # =====================================================

    generated = (
        generate_image_with_gemini(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: GEMINI"
        )

        return generated

    print(
        "Gemini image generation failed."
    )

    # =====================================================
    # 2. Groq - الاحتياطي الأول
    # =====================================================

    generated = (
        generate_image_with_groq(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: GROQ"
        )

        return generated

    print(
        "Groq image generation failed."
    )

    # =====================================================
    # 3. OpenRouter - الاحتياطي الثاني
    # =====================================================

    generated = (
        generate_image_with_openrouter(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: OPENROUTER"
        )

        return generated

    print(
        "OpenRouter image generation failed."
    )

    # =====================================================
    # 4. Mistral - الأخير
    # =====================================================

    generated = (
        generate_image_with_mistral(
            prompt
        )
    )

    if generated:

        print(
            "IMAGE GENERATION SUCCESS: MISTRAL"
        )

        return generated

    print(
        "IMAGE GENERATION FAILED."
    )

    return None


# =========================================================
# كشف طلب إنشاء صورة
# =========================================================

def is_image_generation_request(
    message
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

        "هل يمكنك إنشاء صورة",
        "هل يمكنك انشاء صورة",

        "هل تقدر تنشئ لي صورة",
        "هل تقدر تنشئ صورة",

        "واش تقدر تنشئ لي صورة",
        "واش تقدر تنشئ صورة",

        "ممكن تنشئ لي صورة",
        "ممكن تنشئ صورة",

        "تقدر تنشئ لي صورة",
        "تقدر تنشئ صورة",

        "بغيتك تنشئ لي صورة",
        "بغيتك تصنع لي صورة",
        "بغيتك ترسم لي صورة",

        "اريد صورة",
        "اريد صوره",
        "اريدك تولد صورة",
        "اريدك ان تولد صورة",
        "اريدك تنشئ صورة",
        "اريدك تصنع صورة",

        "ابغى صورة",
        "ابغى صوره",

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

        "create artwork",
        "generate artwork"
    ]

    for phrase in direct_phrases:

        normalized_phrase = normalize_text(
            phrase
        )

        if normalized_phrase in text:

            print(
                "IMAGE GENERATION INTENT DETECTED:",
                text
            )

            return True

    has_image_word = any(
        word in text
        for word in (
            "صورة",
            "صوره",
            "image",
            "picture",
            "artwork"
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
            "تنشأ",
            "تولد",
            "يصنع",
            "يرسم",
            "generate",
            "create",
            "make",
            "draw"
        )
    )

    if (
        has_image_word
        and has_generation_word
    ):

        print(
            "FLEXIBLE IMAGE GENERATION "
            "INTENT DETECTED:",
            text
        )

        return True

    return False


# =========================================================
# استخراج وصف الصورة
# =========================================================

def get_image_prompt(
    message
):

    if not message:
        return ""

    original = str(
        message
    ).strip()

    text = original

    greeting_patterns = [

        r"^السلام عليكم ورحمة الله وبركاته[،,\s]*",
        r"^السلام عليكم ورحمه الله وبركاته[،,\s]*",
        r"^السلام عليكم[،,\s]*",
        r"^مرحبا[،,\s]*",
        r"^مرحباً[،,\s]*",
        r"^اهلا[،,\s]*",
        r"^أهلا[،,\s]*"
    ]

    for pattern in greeting_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

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
        "ابغى"
    ]

    changed = True

    while changed:

        changed = False

        normalized_text = normalize_text(
            text
        )

        for prefix in prefixes:

            normalized_prefix = normalize_text(
                prefix
            )

            if normalized_text.startswith(
                normalized_prefix + " "
            ):

                text = text[
                    len(prefix):
                ].strip()

                changed = True

                break

    action_prefixes = [

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

        "تولد لي",
        "تولد",

        "generate",
        "create",
        "make",
        "draw"
    ]

    changed = True

    while changed:

        changed = False

        normalized_text = normalize_text(
            text
        )

        for prefix in action_prefixes:

            normalized_prefix = normalize_text(
                prefix
            )

            if normalized_text.startswith(
                normalized_prefix + " "
            ):

                text = text[
                    len(prefix):
                ].strip()

                changed = True

                break

    image_prefixes = [

        "صورة",
        "صوره",
        "image",
        "picture"
    ]

    for image_word in image_prefixes:

        normalized_text = normalize_text(
            text
        )

        normalized_image_word = normalize_text(
            image_word
        )

        if normalized_text.startswith(
            normalized_image_word + " "
        ):

            text = text[
                len(image_word):
            ].strip()

            break

    text = text.strip(
        " \t\n\r.,،:؛!?؟"
    )

    normalized_result = normalize_text(
        text
    )

    empty_generation_requests = {

        "",
        "صوره",
        "صورة",
        "image",
        "picture",
        "انشئ",
        "انشئ صوره",
        "انشئ صورة",
        "أنشئ صورة",
        "انشاء صوره",
        "انشاء صورة",
        "توليد صورة",
        "generate image",
        "generate an image",
        "create image",
        "create an image"
    }

    normalized_empty = {
        normalize_text(item)
        for item in empty_generation_requests
    }

    if normalized_result in normalized_empty:

        return (
            "Create a beautiful high-quality "
            "photorealistic image. "
            "Use cinematic lighting, realistic "
            "details, natural composition, "
            "professional photography, "
            "high resolution, 2K or higher."
        )

    text = re.sub(
        r"^(هل يمكنك|هل تقدر|هل تستطيع)\s*",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    if not text:

        return (
            "Create a beautiful high-quality "
            "photorealistic image with "
            "cinematic lighting and realistic "
            "details, high resolution, 2K or higher."
        )

    return text


# =========================================================
# كشف تعديل صورة
# =========================================================

def is_image_edit_request(
    message
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
        "turn it into"
    ]

    for word in edit_words:

        normalized_word = normalize_text(
            word
        )

        if normalized_word in text:

            return True

    return False


# =========================================================
# Prompt تحرير الصورة
# =========================================================

def build_image_edit_prompt(
    image_description,
    edit_request
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
        "Create a new photorealistic image "
        "based on the following source-scene "
        "description.\n\n"

        "SOURCE SCENE:\n"
        f"{description}\n\n"

        "REQUESTED EDIT:\n"
        f"{request}\n\n"

        "IMPORTANT:\n"
        "- Preserve the same overall composition.\n"
        "- Preserve the same camera viewpoint.\n"
        "- Preserve the same environment and background.\n"
        "- Preserve the approximate lighting and weather.\n"
        "- Preserve the position and scale of the main subject.\n"
        "- Change only what the user requested.\n"
        "- Make the result look like a real photograph.\n"
        "- Do not add unrelated objects.\n"
        "- Keep the requested replacement visually coherent "
        "with the original scene.\n"
        "- Render the final image in high resolution."
    )


# =========================================================
# تعديل الصورة
# =========================================================

def edit_image(
    edit_request,
    image_bytes,
    mime_type
):

    if not edit_request:
        return None

    if not image_bytes:
        return None

    print(
        "IMAGE EDIT REQUEST:",
        edit_request
    )

    analysis_prompt = (
        "Describe this image in very detailed "
        "visual terms for a second image model. "
        "Focus on composition, camera angle, "
        "main subject, colors, environment, "
        "background, lighting, shadows, weather, "
        "and spatial relationships. "
        "Do not discuss the requested edit. "
        "Return only the visual description."
    )

    image_description = ask_gemini_image(
        analysis_prompt,
        image_bytes,
        mime_type
    )

    if not image_description:

        image_description = ask_groq_image(
            analysis_prompt,
            image_bytes,
            mime_type
        )

    if not image_description:

        image_description = ask_mistral_image(
            analysis_prompt,
            image_bytes,
            mime_type
        )

    if not image_description:

        print(
            "IMAGE EDIT ERROR: "
            "Could not analyze source image."
        )

        return None

    edit_prompt = build_image_edit_prompt(
        image_description,
        edit_request
    )

    print(
        "IMAGE EDIT PROMPT:",
        edit_prompt
    )

    return generate_image(
        edit_prompt
    )


# =========================================================
# Ido AI - الرد الرئيسي
# =========================================================

def get_response(
    message,
    conversation_id=None,
    save_response=True
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

    # =====================================================
    # توليد الصورة أولًا
    # =====================================================

    if is_image_generation_request(
        original_message
    ):

        print(
            "DIRECT IMAGE GENERATION REQUEST:",
            original_message
        )

        image_prompt = get_image_prompt(
            original_message
        )

        if not image_prompt:

            image_prompt = (
                "Create a beautiful "
                "high-quality image."
            )

        print(
            "FINAL IMAGE PROMPT:",
            image_prompt
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
                    source="image_generation"
                )

            return (
                "IMAGE_URL:"
                + generated
            )

        return (
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة مولدات الصور المتاحة "
            "تلقائيًا، ولكن لم يُرجع أي مولد صورة."
        )

    # =====================================================
    # الردود الثابتة
    # =====================================================

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
                source="builtin"
            )

        return builtin_answer

    # =====================================================
    # سياق المحادثة
    # =====================================================

    model_message = build_context_message(
        original_message,
        conversation_id
    )

    # =====================================================
    # Gemini
    # =====================================================

    answer = ask_gemini(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="gemini"
            )

        return answer

    # =====================================================
    # Groq
    # =====================================================

    print(
        "Gemini failed. "
        "Trying Groq..."
    )

    answer = ask_groq(
        model_message
    )

    if answer:

        if save_response:

            save_ai_response(
                original_message,
                answer,
                conversation_id,
                source="groq"
            )

        return answer

    # =====================================================
    # OpenRouter
    # =====================================================

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
                source="openrouter"
            )

        return answer

    # =====================================================
    # Mistral
    # =====================================================

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
                source="mistral"
            )

        return answer

    # =====================================================
    # فشل الجميع
    # =====================================================

    fallback = (
        "أنا Ido AI ولم أجد إجابة حاليًا."
    )

    if save_response:

        save_ai_response(
            original_message,
            fallback,
            conversation_id,
            source="fallback"
        )

    return fallback


# =========================================================
# تحليل أو تعديل صورة
# =========================================================

def get_image_response(
    message,
    image_bytes,
    mime_type,
    conversation_id=None
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

    # =====================================================
    # تعديل الصورة
    # =====================================================

    if is_image_edit_request(
        message
    ):

        generated_image = edit_image(
            message,
            image_bytes,
            mime_type
        )

        if generated_image:

            if conversation_id:

                save_ai_response(
                    message,
                    "تم تعديل الصورة بناءً على طلبك.",
                    conversation_id,
                    source="image_edit"
                )

            return (
                "IMAGE_URL:"
                + generated_image
            )

        return (
            "تعذر تعديل الصورة حاليًا."
        )

    # =====================================================
    # Gemini Vision
    # =====================================================

    print(
        "Trying Gemini Vision..."
    )

    answer = ask_gemini_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="gemini_vision"
            )

        return answer

    # =====================================================
    # Groq Vision
    # =====================================================

    print(
        "Gemini Vision failed. "
        "Trying Groq Vision..."
    )

    answer = ask_groq_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="groq_vision"
            )

        return answer

    # =====================================================
    # Mistral Vision
    # =====================================================

    print(
        "Groq Vision failed. "
        "Trying Mistral Vision..."
    )

    answer = ask_mistral_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:

        if conversation_id:

            save_ai_response(
                message,
                answer,
                conversation_id,
                source="mistral_vision"
            )

        return answer

    # =====================================================
    # فشل
    # =====================================================

    fallback = (
        "تعذر تحليل الصورة حاليًا."
    )

    if conversation_id:

        save_ai_response(
            message,
            fallback,
            conversation_id,
            source="image_fallback"
        )

    return fallback