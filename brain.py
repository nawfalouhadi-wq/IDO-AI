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
# تحميل متغيرات البيئة
# ============================================================

load_dotenv()


# ============================================================
# إعدادات عامة
# ============================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "5")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "30")),
)

IMAGE_TIMEOUT = (
    int(os.getenv("IMAGE_CONNECT_TIMEOUT", "10")),
    int(os.getenv("IMAGE_READ_TIMEOUT", "120")),
)

CONVERSATION_CONTEXT_LIMIT = int(
    os.getenv("CONVERSATION_CONTEXT_LIMIT", "12")
)


# ============================================================
# إعدادات الملفات والصور
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


IMAGE_RESOLUTION = os.getenv(
    "IMAGE_RESOLUTION",
    "2K",
).upper()


# ============================================================
# النماذج
# ============================================================

# ----------------------------
# Groq
# ----------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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


# ----------------------------
# Mistral
# ----------------------------

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MISTRAL_URL = (
    "https://api.mistral.ai/v1/chat/completions"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

MISTRAL_VISION_MODEL = os.getenv(
    "MISTRAL_VISION_MODEL",
    "pixtral-12b-2409",
)


# ----------------------------
# OpenRouter
# ----------------------------

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "",
)


# ============================================================
# ملاحظة مهمة
#
# Gemini و xAI/Grok غير موجودين في Routes هذه النسخة.
#
# السبب:
# Gemini = quota exhausted
# xAI/Grok = credits / spending limit exhausted
#
# لذلك لن نرسل أي Request إليهما.
# ============================================================

print("=================================================")
print("BRAIN.PY LOADED")
print("TEXT ROUTE: GROQ -> MISTRAL -> OPENROUTER")
print("VISION ROUTE: GROQ -> MISTRAL")
print("IMAGE ROUTE: MISTRAL -> OPENROUTER")
print("GEMINI: DISABLED")
print("XAI / GROK: DISABLED")
print("IMAGE RESOLUTION:", IMAGE_RESOLUTION)
print("=================================================")


# ============================================================
# حالة الخدمات
# ============================================================

if GROQ_API_KEY:
    print("GROQ CLIENT: READY")
    print("GROQ MODEL:", GROQ_MODEL)
    print("GROQ VISION MODEL:", GROQ_VISION_MODEL)
else:
    print("GROQ_API_KEY: NOT FOUND")


if MISTRAL_API_KEY:
    print("MISTRAL CLIENT: READY")
    print("MISTRAL MODEL:", MISTRAL_MODEL)
    print("MISTRAL VISION MODEL:", MISTRAL_VISION_MODEL)
else:
    print("MISTRAL_API_KEY: NOT FOUND")


if OPENROUTER_API_KEY:
    print("OPENROUTER CLIENT: READY")
else:
    print("OPENROUTER_API_KEY: NOT FOUND")


# ============================================================
# تنظيف الإجابة
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
# تطبيع النص العربي
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
        text = text.replace(old, new)

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
# الردود السريعة
# ============================================================

BUILTIN_RESPONSES = {
    "hello": (
        "السلام عليكم ورحمة الله وبركاته. "
        "أنا Ido AI، كيف يمكنني مساعدتك؟"
    ),

    "hi": (
        "السلام عليكم ورحمة الله وبركاته. "
        "أنا Ido AI، كيف يمكنني مساعدتك؟"
    ),

    "مرحبا": (
        "السلام عليكم ورحمة الله وبركاته. "
        "مرحبًا بك، كيف يمكنني مساعدتك؟"
    ),

    "سلام": (
        "وعليكم السلام ورحمة الله وبركاته. "
        "كيف يمكنني مساعدتك؟"
    ),

    "السلام عليكم": (
        "وعليكم السلام ورحمة الله وبركاته. "
        "كيف يمكنني مساعدتك؟"
    ),

    "السلام عليكم ورحمة الله وبركاته": (
        "وعليكم السلام ورحمة الله وبركاته. "
        "كيف يمكنني مساعدتك؟"
    ),

    "اسمك": "أنا Ido AI.",

    "ما اسمك": "أنا Ido AI.",

    "كيف حالك": (
        "أنا بخير، شكرًا لسؤالك. "
        "كيف يمكنني مساعدتك؟"
    ),

    "من صنعك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من طورك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من بناك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من هو مطورك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من برمجك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من اخترعك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من انشاك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من صممك": (
        "تم تطويري وبنائي بواسطة "
        "Noufal Ouhadi، وأنا Ido AI."
    ),

    "من صنع ido ai": (
        "تم تطوير Ido AI وبناؤه "
        "بواسطة Noufal Ouhadi."
    ),

    "من طور ido ai": (
        "تم تطوير Ido AI بواسطة "
        "Noufal Ouhadi."
    ),

    "ما هو الذكاء الاصطناعي": (
        "الذكاء الاصطناعي هو مجال من علوم "
        "الحاسوب يهدف إلى تطوير أنظمة قادرة "
        "على فهم المعلومات والتعلم منها "
        "وتنفيذ مهام تحتاج عادةً إلى قدر "
        "من الذكاء البشري."
    ),

    "ما هي بايثون": (
        "Python هي لغة برمجة قوية وسهلة "
        "الاستخدام، وتُستخدم في تطوير "
        "البرامج والذكاء الاصطناعي "
        "وتحليل البيانات."
    ),

    "ما هي عاصمة المغرب": "عاصمة المغرب هي الرباط.",

    "ما هي عاصمة فرنسا": "عاصمة فرنسا هي باريس.",

    "شكرا": "على الرحب والسعة.",

    "وداعا": "إلى اللقاء! أتمنى لك يومًا سعيدًا.",
}


# ============================================================
# سياق المحادثة
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
        print("CONVERSATION CONTEXT ERROR:", e)
        context = ""

    if not context:
        return message

    return (
        "أنت Ido AI، مساعد ذكاء اصطناعي متعدد اللغات.\n\n"
        "استخدم سياق المحادثة السابقة عندما يكون "
        "مفيدًا لفهم الرسالة الجديدة.\n"
        "لا تكرر سياق المحادثة للمستخدم.\n\n"
        "## سياق المحادثة:\n"
        f"{context}\n\n"
        "## الرسالة الجديدة:\n"
        f"{message}\n\n"
        "أجب بشكل طبيعي ومباشر."
    )


# ============================================================
# حفظ الإجابة
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
        print("MEMORY LEARN ERROR:", e)

    if conversation_id:
        try:
            add_conversation_message(
                question,
                answer,
                conversation_id=conversation_id,
            )

        except Exception as e:
            print("CONVERSATION SAVE ERROR:", e)


# ============================================================
# استخراج محتوى Chat Completions
# ============================================================

def extract_response_content(data):
    if not isinstance(data, dict):
        return None

    choices = data.get("choices", [])

    if not choices:
        return None

    choice = choices[0]

    if not isinstance(choice, dict):
        return None

    message_data = choice.get("message", {})

    if not isinstance(message_data, dict):
        return None

    content = message_data.get("content")

    if isinstance(content, str):
        return clean_answer(content)

    if isinstance(content, list):
        parts = []

        for item in content:
            if not isinstance(item, dict):
                continue

            text = item.get("text")

            if text:
                parts.append(str(text))

        if parts:
            return clean_answer(
                "\n".join(parts)
            )

    return None


# ============================================================
# استخراج URLs من أي استجابة
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

    if isinstance(value, str):
        urls = re.findall(
            r"https?://[^\s\"'<>]+",
            value,
        )

        for url in urls:
            url = url.rstrip(
                ".,);]"
            )

            if url not in found:
                found.append(url)

        return found

    if isinstance(value, dict):
        for item in value.values():
            extract_image_urls_deep(
                item,
                found,
                depth + 1,
            )

        return found

    if isinstance(value, (list, tuple)):
        for item in value:
            extract_image_urls_deep(
                item,
                found,
                depth + 1,
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
        "image_url",
    ):
        try:
            item = getattr(
                value,
                attribute,
                None,
            )

        except Exception:
            item = None

        if item is not None:
            extract_image_urls_deep(
                item,
                found,
                depth + 1,
            )

    return found


# ============================================================
# حفظ صورة Base64
# ============================================================

def save_generated_image(image_bytes):
    if not image_bytes:
        return None

    try:
        filename = (
            "aido_generated_"
            f"{uuid.uuid4().hex}.png"
        )

        file_path = (
            GENERATED_IMAGE_DIR / filename
        )

        file_path.write_bytes(image_bytes)

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
# استخراج Base64
# ============================================================

def extract_base64_images(data):
    found = []

    if data is None:
        return found

    if isinstance(data, dict):
        for key, value in data.items():
            key_text = str(key).lower()

            if key_text in (
                "b64_json",
                "base64",
                "image_base64",
            ):
                if (
                    isinstance(value, str)
                    and value.strip()
                ):
                    found.append(
                        value.strip()
                    )

            else:
                found.extend(
                    extract_base64_images(value)
                )

        return found

    if isinstance(data, list):
        for item in data:
            found.extend(
                extract_base64_images(item)
            )

        return found

    return found


# ============================================================
# Groq - النص
#
# Groq يعمل عندك الآن ويرجع 200.
# لذلك هو أول مزود.
# ============================================================

def ask_groq(message):
    if not GROQ_API_KEY:
        return None

    if not message:
        return None

    try:
        print("Trying Groq...")

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization":
                    f"Bearer {GROQ_API_KEY}",

                "Content-Type":
                    "application/json",
            },
            json={
                "model": GROQ_MODEL,

                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Ido AI. "
                            "Answer naturally and accurately. "
                            "Use the language of the user. "
                            "For Arabic, answer in clear Arabic."
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],

                "temperature": 0.7,

                "max_completion_tokens": 1024,
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

        return None

    except requests.exceptions.Timeout:
        print("Groq ERROR: timeout.")
        return None

    except requests.exceptions.ConnectionError:
        print("Groq ERROR: connection failed.")
        return None

    except Exception as e:
        print("Groq ERROR:", e)
        return None


# ============================================================
# Groq - Vision
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
        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        print("Trying Groq Vision...")

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization":
                    f"Bearer {GROQ_API_KEY}",

                "Content-Type":
                    "application/json",
            },
            json={
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
                                    "url":
                                        image_data_url,
                                },
                            },
                        ],
                    }
                ],

                "temperature": 0.5,

                "max_completion_tokens": 1024,
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

    except requests.exceptions.Timeout:
        print("Groq Vision ERROR: timeout.")
        return None

    except Exception as e:
        print("Groq Vision ERROR:", e)
        return None


# ============================================================
# Mistral - النص
# ============================================================

def ask_mistral(message):
    if not MISTRAL_API_KEY:
        return None

    if not message:
        return None

    try:
        print("Trying Mistral...")

        response = requests.post(
            MISTRAL_URL,
            headers={
                "Authorization":
                    f"Bearer {MISTRAL_API_KEY}",

                "Content-Type":
                    "application/json",
            },
            json={
                "model": MISTRAL_MODEL,

                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Ido AI. "
                            "Answer accurately and naturally. "
                            "Use the user's language."
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],

                "temperature": 0.7,

                "max_tokens": 1024,
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

        return None

    except requests.exceptions.Timeout:
        print("Mistral ERROR: timeout.")
        return None

    except requests.exceptions.ConnectionError:
        print(
            "Mistral ERROR: connection failed."
        )
        return None

    except Exception as e:
        print("Mistral ERROR:", e)
        return None


# ============================================================
# Mistral - Vision
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
        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        print("Trying Mistral Vision...")

        response = requests.post(
            MISTRAL_URL,
            headers={
                "Authorization":
                    f"Bearer {MISTRAL_API_KEY}",

                "Content-Type":
                    "application/json",
            },
            json={
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
                                "image_url": {
                                    "url":
                                        image_data_url,
                                },
                            },
                        ],
                    }
                ],

                "temperature": 0.5,

                "max_tokens": 1024,
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

    except requests.exceptions.Timeout:
        print("Mistral Vision ERROR: timeout.")
        return None

    except Exception as e:
        print("Mistral Vision ERROR:", e)
        return None


# ============================================================
# OpenRouter - النص
#
# يتم استخدامه فقط إذا كان المفتاح موجودًا.
# ============================================================

def ask_openrouter(message):
    if not OPENROUTER_API_KEY:
        return None

    if not message:
        return None

    try:
        print("Trying OpenRouter...")

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
                "model": "openrouter/free",

                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            },
            timeout=(
                5,
                30,
            ),
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

    except requests.exceptions.Timeout:
        print("OpenRouter ERROR: timeout.")
        return None

    except requests.exceptions.ConnectionError:
        print(
            "OpenRouter ERROR: connection failed."
        )
        return None

    except Exception as e:
        print("OpenRouter ERROR:", e)
        return None


# ============================================================
# كشف طلب إنشاء صورة
# ============================================================

def is_image_generation_request(message):
    text = normalize_text(message)

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
        "اريد صورة",
        "اريد صوره",
        "اريدك تولد صورة",
        "اريدك ان تولد صورة",
        "اريدك تنشئ صورة",
        "اريدك تصنع صورة",
        "بغيتك تنشئ لي صورة",
        "بغيتك تصنع لي صورة",
        "بغيتك ترسم لي صورة",
        "واش تقدر تنشئ صورة",
        "ممكن تنشئ صورة",
        "تقدر تنشئ صورة",
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
        if normalize_text(phrase) in text:
            print(
                "IMAGE GENERATION INTENT DETECTED:",
                message,
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
# استخراج وصف الصورة
# ============================================================

def get_image_prompt(message):
    if not message:
        return ""

    text = str(message).strip()

    greetings = [
        r"^السلام عليكم ورحمة الله وبركاته[،,\s]*",
        r"^السلام عليكم[،,\s]*",
        r"^مرحبا[،,\s]*",
        r"^مرحباً[،,\s]*",
        r"^اهلا[،,\s]*",
        r"^أهلا[،,\s]*",
        r"^حسنا[،,\s]*",
        r"^حسنًا[،,\s]*",
    ]

    for pattern in greetings:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
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
        "ابغى",
    ]

    changed = True

    while changed:
        changed = False

        normalized_text = normalize_text(text)

        for prefix in prefixes:
            normalized_prefix = normalize_text(
                prefix
            )

            if normalized_text.startswith(
                normalized_prefix + " "
            ):
                text = text[len(prefix):].strip()
                changed = True
                break

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
        "تولد لي",
        "تولد",
        "generate",
        "create",
        "make",
        "draw",
    ]

    changed = True

    while changed:
        changed = False

        normalized_text = normalize_text(text)

        for prefix in actions:
            normalized_prefix = normalize_text(
                prefix
            )

            if normalized_text.startswith(
                normalized_prefix + " "
            ):
                text = text[len(prefix):].strip()
                changed = True
                break

    image_words = [
        "صورة",
        "صوره",
        "image",
        "picture",
    ]

    for word in image_words:
        if normalize_text(text).startswith(
            normalize_text(word) + " "
        ):
            text = text[len(word):].strip()
            break

    text = text.strip(
        " \t\n\r.,،:؛!?؟"
    )

    if not text:
        return (
            "Create a beautiful high-quality "
            "photorealistic image with realistic "
            "details, cinematic lighting, "
            "professional composition, "
            "high resolution."
        )

    return text


# ============================================================
# كشف تعديل صورة
# ============================================================

def is_image_edit_request(message):
    text = normalize_text(message)

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
        normalize_text(word) in text
        for word in edit_words
    )


# ============================================================
# Mistral Image Generation
#
# Mistral يدعم image_generation كـ tool
# داخل Chat Completions.
# ============================================================

def generate_image_with_mistral(prompt):
    if not MISTRAL_API_KEY:
        print(
            "MISTRAL IMAGE: API KEY NOT FOUND"
        )
        return None

    if not prompt:
        return None

    try:
        print(
            "MISTRAL IMAGE GENERATION STARTED"
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
                "model": MISTRAL_MODEL,

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
            },
            timeout=IMAGE_TIMEOUT,
        )

        print(
            "Mistral Image Status:",
            response.status_code,
        )

        if response.status_code != 200:
            print(
                "Mistral Image Response:",
                response.text[:3000],
            )
            return None

        data = response.json()

        # ----------------------------------------------------
        # محاولة استخراج URL
        # ----------------------------------------------------

        image_urls = (
            extract_image_urls_deep(data)
        )

        for url in image_urls:
            if (
                "files.mistral.ai" in url
                or "image" in url.lower()
                or "generated" in url.lower()
            ):
                print(
                    "MISTRAL IMAGE URL:",
                    url,
                )
                return url

        # ----------------------------------------------------
        # محاولة استخراج Base64
        # ----------------------------------------------------

        base64_images = (
            extract_base64_images(data)
        )

        for encoded_image in base64_images:
            try:
                if "," in encoded_image:
                    encoded_image = (
                        encoded_image.split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = base64.b64decode(
                    encoded_image
                )

                image_url = save_generated_image(
                    image_bytes
                )

                if image_url:
                    print(
                        "MISTRAL IMAGE SAVED:",
                        image_url,
                    )
                    return image_url

            except Exception as e:
                print(
                    "MISTRAL BASE64 ERROR:",
                    e,
                )

        print(
            "MISTRAL IMAGE: "
            "No image URL/base64 found."
        )

        print(
            "MISTRAL IMAGE DATA:",
            str(data)[:5000],
        )

        return None

    except requests.exceptions.Timeout:
        print(
            "MISTRAL IMAGE ERROR: timeout."
        )
        return None

    except requests.exceptions.ConnectionError:
        print(
            "MISTRAL IMAGE ERROR: connection failed."
        )
        return None

    except Exception as e:
        print(
            "MISTRAL IMAGE ERROR:",
            e,
        )
        return None


# ============================================================
# OpenRouter Image
#
# يتم تشغيله فقط إذا قمت بوضع
# OPENROUTER_IMAGE_MODEL
# ============================================================

def generate_image_with_openrouter(prompt):
    if not OPENROUTER_API_KEY:
        return None

    if not OPENROUTER_IMAGE_MODEL:
        print(
            "OPENROUTER IMAGE: NOT CONFIGURED"
        )
        return None

    if not prompt:
        return None

    try:
        print(
            "OPENROUTER IMAGE GENERATION STARTED"
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
                    OPENROUTER_IMAGE_MODEL,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
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

        # Base64
        for encoded_image in extract_base64_images(
            data
        ):
            try:
                if "," in encoded_image:
                    encoded_image = (
                        encoded_image.split(
                            ",",
                            1,
                        )[1]
                    )

                image_bytes = base64.b64decode(
                    encoded_image
                )

                image_url = save_generated_image(
                    image_bytes
                )

                if image_url:
                    return image_url

            except Exception:
                continue

        # URL
        urls = extract_image_urls_deep(data)

        if urls:
            return urls[0]

        return None

    except requests.exceptions.Timeout:
        print(
            "OpenRouter Image ERROR: timeout."
        )
        return None

    except Exception as e:
        print(
            "OpenRouter Image ERROR:",
            e,
        )
        return None


# ============================================================
# مولد الصور الرئيسي
#
# لا Gemini
# لا Grok
# لا Groq
#
# Mistral -> OpenRouter
# ============================================================

def generate_image(prompt):
    if not prompt:
        return None

    prompt = str(prompt).strip()

    if not prompt:
        return None

    print("=================================================")
    print("IMAGE GENERATION STARTED")
    print("IMAGE PROMPT:", prompt)
    print("IMAGE ROUTE: MISTRAL -> OPENROUTER")
    print("=================================================")

    # --------------------------------------------------------
    # 1. Mistral
    # --------------------------------------------------------

    generated = generate_image_with_mistral(
        prompt
    )

    if generated:
        print(
            "IMAGE GENERATION SUCCESS: MISTRAL"
        )
        return generated

    # --------------------------------------------------------
    # 2. OpenRouter
    # --------------------------------------------------------

    generated = generate_image_with_openrouter(
        prompt
    )

    if generated:
        print(
            "IMAGE GENERATION SUCCESS: OPENROUTER"
        )
        return generated

    # --------------------------------------------------------
    # فشل
    # --------------------------------------------------------

    print(
        "IMAGE GENERATION FAILED."
    )

    return None


# ============================================================
# بناء Prompt تعديل الصورة
# ============================================================

def build_image_edit_prompt(
    image_description,
    edit_request,
):
    description = (
        image_description
        or
        "A realistic scene containing "
        "the main subject from the original image."
    )

    request = (
        edit_request
        or
        "Keep the scene unchanged."
    )

    return (
        "Create a photorealistic image "
        "based on this source scene.\n\n"

        "SOURCE SCENE:\n"
        f"{description}\n\n"

        "REQUESTED EDIT:\n"
        f"{request}\n\n"

        "IMPORTANT:\n"
        "- Preserve the original composition.\n"
        "- Preserve the camera viewpoint.\n"
        "- Preserve the environment.\n"
        "- Preserve the background.\n"
        "- Preserve lighting and shadows.\n"
        "- Preserve the main subject's position "
        "and approximate scale.\n"
        "- Change only what the user requested.\n"
        "- Do not add unrelated objects.\n"
        "- Make the result realistic and coherent.\n"
        "- Render in high quality."
    )


# ============================================================
# تحليل الصورة قبل التعديل
#
# Groq -> Mistral
# ============================================================

def describe_image(
    image_bytes,
    mime_type,
):
    analysis_prompt = (
        "Describe this image in detailed visual terms. "
        "Describe the main subject, composition, "
        "camera viewpoint, environment, background, "
        "colors, lighting, shadows, weather, "
        "and spatial relationships. "
        "Return only the visual description."
    )

    description = ask_groq_image(
        analysis_prompt,
        image_bytes,
        mime_type,
    )

    if description:
        return description

    return ask_mistral_image(
        analysis_prompt,
        image_bytes,
        mime_type,
    )


# ============================================================
# تعديل صورة
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

    image_description = describe_image(
        image_bytes,
        mime_type,
    )

    if not image_description:
        print(
            "IMAGE EDIT ERROR: "
            "Could not analyze source image."
        )
        return None

    edit_prompt = build_image_edit_prompt(
        image_description,
        edit_request,
    )

    print(
        "IMAGE EDIT PROMPT:",
        edit_prompt,
    )

    return generate_image(
        edit_prompt
    )


# ============================================================
# Ido AI - الرد الرئيسي
# ============================================================

def get_response(
    message,
    conversation_id=None,
    save_response=True,
):
    if not message:
        return "اكتب رسالة أولًا."

    original_message = str(
        message
    ).strip()

    if not original_message:
        return "اكتب رسالة أولًا."

    # ========================================================
    # إنشاء صورة
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

        print(
            "FINAL IMAGE PROMPT:",
            image_prompt,
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
            "لم يُرجع مزود الصور المتاح صورة."
        )

    # ========================================================
    # الردود الثابتة
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
    # سياق المحادثة
    # ========================================================

    model_message = build_context_message(
        original_message,
        conversation_id,
    )

    # ========================================================
    # 1. Groq
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
    # 2. Mistral
    # ========================================================

    print(
        "Groq failed. Trying Mistral..."
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
    # 3. OpenRouter
    # ========================================================

    print(
        "Mistral failed. "
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
    # فشل جميع مزودي النص
    # ========================================================

    fallback = (
        "أنا Ido AI ولم أتمكن من الحصول "
        "على إجابة من مزودي الذكاء الاصطناعي "
        "المتاحين حاليًا."
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
# تحليل أو تعديل صورة
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

    if not mime_type.startswith("image/"):
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
    # تعديل الصورة
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
    # 1. Groq Vision
    # ========================================================

    print(
        "IMAGE ANALYSIS ROUTE: "
        "GROQ -> MISTRAL"
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
    # 2. Mistral Vision
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
    # فشل
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