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

try:
    from mistralai.client import Mistral
    from mistralai.client.models import ToolFileChunk
except Exception:
    Mistral = None
    ToolFileChunk = None


# =========================================================
# تحميل ملف .env
# =========================================================

load_dotenv()


# =========================================================
# إعدادات عامة
# =========================================================

REQUEST_TIMEOUT = (
    int(os.getenv("REQUEST_CONNECT_TIMEOUT", "5")),
    int(os.getenv("REQUEST_READ_TIMEOUT", "30"))
)


# =========================================================
# مهلة OpenRouter الخاصة
# =========================================================

OPENROUTER_TIMEOUT = (
    int(os.getenv("OPENROUTER_CONNECT_TIMEOUT", "5")),
    int(os.getenv("OPENROUTER_READ_TIMEOUT", "15"))
)


# =========================================================
# إعدادات سياق المحادثة
# =========================================================

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

        print(
            "GEMINI CLIENT: READY"
        )

        print(
            "GEMINI MODEL:",
            GEMINI_MODEL
        )

        print(
            "GEMINI TIMEOUT:",
            "30 seconds"
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

if OPENROUTER_API_KEY:

    print(
        "OPENROUTER CLIENT: READY"
    )

    print(
        "OPENROUTER TIMEOUT:",
        OPENROUTER_TIMEOUT
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

MISTRAL_IMAGE_MODEL = os.getenv(
    "MISTRAL_IMAGE_MODEL",
    "mistral-medium-latest"
)

mistral_client = None

if MISTRAL_API_KEY:

    if Mistral is not None:

        try:

            mistral_client = Mistral(
                api_key=MISTRAL_API_KEY
            )

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

            print(
                "MISTRAL IMAGE MODEL:",
                MISTRAL_IMAGE_MODEL
            )

        except Exception as e:

            print(
                "MISTRAL CLIENT ERROR:",
                e
            )

            mistral_client = None

    else:

        print(
            "MISTRAL CLIENT ERROR: "
            "mistralai package غير مثبت."
        )

else:

    print(
        "MISTRAL_API_KEY: NOT FOUND"
    )


# =========================================================
# Mistral Image Generation Agent
# =========================================================

mistral_image_agent = None

if mistral_client is not None:

    try:

        mistral_image_agent = (
            mistral_client.beta.agents.create(
                model=MISTRAL_IMAGE_MODEL,
                name="Ido AI Image Generator",
                description=(
                    "Ido AI image generation agent."
                ),
                instructions=(
                    "Use the image generation tool "
                    "when you have to create images."
                ),
                tools=[
                    {
                        "type": "image_generation"
                    }
                ],
                completion_args={
                    "temperature": 0.3,
                    "top_p": 0.95
                }
            )
        )

        print(
            "MISTRAL IMAGE AGENT: READY"
        )

    except Exception as e:

        print(
            "MISTRAL IMAGE AGENT ERROR:",
            e
        )

        mistral_image_agent = None


# =========================================================
# معلومات التشغيل
# =========================================================

print(
    "BRAIN.PY LOADED - "
    "GEMINI + OPENROUTER + GROQ + MISTRAL READY"
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
# تطبيع النص العربي والإنجليزي
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
# بناء رسالة تحتوي على سياق المحادثة
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
# حفظ إجابة المحادثة
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
# استخراج محتوى الاستجابة
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

    return clean_answer(
        message_data.get(
            "content"
        )
    )


# =========================================================
# حفظ الصورة الناتجة
# =========================================================

def save_generated_image(
    image_bytes
):

    if not image_bytes:
        return None

    try:

        filename = (
            f"aido_generated_"
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
# استخراج File IDs من استجابة Mistral
# =========================================================

def extract_generated_images(
    response
):

    file_ids = []

    if response is None:

        print(
            "MISTRAL IMAGE DEBUG: "
            "Response is None."
        )

        return file_ids

    try:

        outputs = getattr(
            response,
            "outputs",
            None
        )

        if not outputs:

            print(
                "MISTRAL IMAGE DEBUG: "
                "No outputs found."
            )

            return file_ids

        print(
            "MISTRAL IMAGE DEBUG:",
            len(outputs),
            "output(s) received."
        )

        latest_output = outputs[-1]

        latest_content = getattr(
            latest_output,
            "content",
            None
        )

        if latest_content:

            for index, chunk in enumerate(
                latest_content
            ):

                chunk_type = getattr(
                    chunk,
                    "type",
                    None
                )

                file_id = getattr(
                    chunk,
                    "file_id",
                    None
                )

                if (
                    ToolFileChunk is not None
                    and isinstance(
                        chunk,
                        ToolFileChunk
                    )
                ):

                    if chunk.file_id:
                        file_ids.append(
                            chunk.file_id
                        )

                    continue

                if (
                    chunk_type == "tool_file"
                    and file_id
                ):

                    file_ids.append(
                        file_id
                    )

        if not file_ids:

            for output in outputs:

                content = getattr(
                    output,
                    "content",
                    None
                )

                if not content:
                    continue

                for chunk in content:

                    chunk_type = getattr(
                        chunk,
                        "type",
                        None
                    )

                    file_id = getattr(
                        chunk,
                        "file_id",
                        None
                    )

                    if (
                        ToolFileChunk is not None
                        and isinstance(
                            chunk,
                            ToolFileChunk
                        )
                    ):

                        if chunk.file_id:
                            file_ids.append(
                                chunk.file_id
                            )

                        continue

                    if (
                        chunk_type == "tool_file"
                        and file_id
                    ):

                        file_ids.append(
                            file_id
                        )

        file_ids = list(
            dict.fromkeys(
                file_ids
            )
        )

        print(
            "MISTRAL IMAGE FILE IDS:",
            file_ids
        )

        return file_ids

    except Exception as e:

        print(
            "EXTRACT GENERATED IMAGES ERROR:",
            e
        )

        return file_ids


# =========================================================
# Gemini - نص
# =========================================================

def ask_gemini(message):

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
# OpenRouter - نص
# =========================================================

def ask_openrouter(message):

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

        return extract_response_content(
            response.json()
        )

    except requests.exceptions.Timeout:

        print(
            "OpenRouter ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "OpenRouter ERROR: "
            "connection failed."
        )

        return None

    except Exception as e:

        print(
            "OpenRouter ERROR:",
            e
        )

        return None


# =========================================================
# Groq - نص
# =========================================================

def ask_groq(message):

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

        return extract_response_content(
            response.json()
        )

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
# Mistral - نص
# =========================================================

def ask_mistral(message):

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

        return extract_response_content(
            response.json()
        )

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
            "Mistral IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# توليد صورة جديدة
# =========================================================

def generate_image(prompt):

    if not prompt:
        return None

    prompt = str(
        prompt
    ).strip()

    if not prompt:
        return None

    if mistral_client is None:

        print(
            "IMAGE GENERATION ERROR: "
            "Mistral client غير جاهز."
        )

        return None

    try:

        print(
            "IMAGE GENERATION STARTED"
        )

        print(
            "IMAGE PROMPT:",
            prompt
        )

        response = (
            mistral_client.beta.conversations.start(
                model=MISTRAL_IMAGE_MODEL,
                inputs=prompt,
                tools=[
                    {
                        "type":
                            "image_generation"
                    }
                ]
            )
        )

        outputs = getattr(
            response,
            "outputs",
            None
        )

        if not outputs:

            print(
                "MISTRAL IMAGE ERROR: "
                "No outputs returned."
            )

            return None

        file_ids = (
            extract_generated_images(
                response
            )
        )

        if not file_ids:

            print(
                "MISTRAL IMAGE ERROR: "
                "No generated image file found."
            )

            return None

        for file_id in file_ids:

            downloaded = (
                mistral_client.files.download(
                    file_id=file_id
                )
            )

            if hasattr(
                downloaded,
                "read"
            ):

                image_bytes = downloaded.read()

            else:

                image_bytes = downloaded

            if not image_bytes:
                continue

            image_url = (
                save_generated_image(
                    image_bytes
                )
            )

            if image_url:

                print(
                    "GENERATED IMAGE SAVED:",
                    image_url
                )

                return image_url

        return None

    except Exception as e:

        print(
            "MISTRAL IMAGE GENERATION ERROR:",
            e
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
        "ولّد لي صورة",
        "ولّد صورة",

        "انشئ لي صورة",
        "انشئ صورة",
        "أنشئ لي صورة",
        "أنشئ صورة",

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
        "هل يمكنك إنشاء لي صورة",
        "هل يمكنك انشاء لي صورة",

        "هل تقدر تنشئ لي صورة",
        "هل تقدر تنشأ لي صورة",
        "هل تقدر تنشئ صورة",
        "هل تقدر تنشأ صورة",

        "واش تقدر تنشئ لي صورة",
        "واش تقدر تنشأ لي صورة",
        "واش تقدر تنشئ صورة",
        "واش تقدر تنشأ صورة",

        "ممكن تنشئ لي صورة",
        "ممكن تنشأ لي صورة",
        "ممكن تنشئ صورة",
        "ممكن تنشأ صورة",

        "تقدر تنشئ لي صورة",
        "تقدر تنشأ لي صورة",

        "بغيتك تنشئ لي صورة",
        "بغيتك تنشأ لي صورة",
        "بغيتك تصنع لي صورة",
        "بغيتك ترسم لي صورة",

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
        "draw a picture"
    ]

    for phrase in direct_phrases:

        if phrase in text:

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
            "ولّد",
            "انشئ",
            "أنشئ",
            "انشاء",
            "إنشاء",
            "اصنع",
            "ارسم",
            "صمم",
            "اعمل",
            "توليد",
            "تنشئ",
            "تنشأ",
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

    text = str(
        message
    ).strip()

    normalized = normalize_text(
        text
    )

    # -----------------------------------------------------
    # إزالة صيغة السؤال أولًا
    # -----------------------------------------------------

    question_prefixes = [

        "هل يمكنك",
        "هل تقدر",
        "هل تستطيع",
        "واش تقدر",
        "واش ممكن",
        "ممكن",
        "تقدر",
        "تستطيع",
        "بغيتك"
    ]

    for prefix in question_prefixes:

        normalized_prefix = normalize_text(
            prefix
        )

        if normalized.startswith(
            normalized_prefix + " "
        ):

            text = text[
                len(prefix):
            ].strip()

            normalized = normalize_text(
                text
            )

            break

    # -----------------------------------------------------
    # إزالة أفعال الإنشاء
    # -----------------------------------------------------

    action_prefixes = [

        "ولد لي",
        "ولد",
        "ولّد لي",
        "ولّد",

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
        "تنشأ لي",
        "تنشأ",

        "generate",
        "create",
        "make",
        "draw"
    ]

    for prefix in action_prefixes:

        normalized_text = normalize_text(
            text
        )

        normalized_prefix = normalize_text(
            prefix
        )

        if normalized_text.startswith(
            normalized_prefix + " "
        ):

            text = text[
                len(prefix):
            ].strip()

            break

    # -----------------------------------------------------
    # إزالة كلمة صورة في البداية
    # -----------------------------------------------------

    for image_word in (
        "صورة",
        "صوره",
        "picture",
        "image"
    ):

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

    text = text.strip()

    if not text:
        return message

    return text


# =========================================================
# كشف طلب تعديل صورة
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
        "حوّل",

        "edit",
        "modify",
        "change",
        "replace",
        "transform",
        "make it",
        "turn it into"
    ]

    for word in edit_words:

        if normalize_text(
            word
        ) in text:

            return True

    return False


# =========================================================
# بناء Prompt خاص بتحرير صورة
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

    return f"""
Create a new photorealistic image based on
the following source-scene description.

SOURCE SCENE:
{description}

REQUESTED EDIT:
{request}

IMPORTANT:

- Preserve the same overall composition.
- Preserve the same camera viewpoint.
- Preserve the same environment and background.
- Preserve the approximate lighting and weather.
- Preserve the position and scale of the main subject.
- Change only what the user requested.
- Make the result look like a real photograph.
- Do not add unrelated objects.
- Keep the requested replacement visually coherent
  with the original scene.
""".strip()


# =========================================================
# تعديل صورة بالاعتماد على تحليلها
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

    image_description = (
        ask_mistral_image(
            analysis_prompt,
            image_bytes,
            mime_type
        )
    )

    if not image_description:

        image_description = (
            ask_groq_image(
                analysis_prompt,
                image_bytes,
                mime_type
            )
        )

    if not image_description:

        print(
            "IMAGE EDIT ERROR: "
            "Could not analyze source image."
        )

        return None

    edit_prompt = (
        build_image_edit_prompt(
            image_description,
            edit_request
        )
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
        return "اكتب رسالة أولًا."

    original_message = str(
        message
    ).strip()

    if not original_message:
        return "اكتب رسالة أولًا."

    # =====================================================
    # إنشاء صورة من الصفر أولًا
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
            image_prompt = original_message

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
            "تحقق من أن Mistral Image Generation "
            "يعمل بشكل صحيح."
        )

    # =====================================================
    # الردود الثابتة
    # =====================================================

    normalized_message = normalize_text(
        original_message
    )

    builtin_answer = BUILTIN_RESPONSES.get(
        normalized_message
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
    # OpenRouter
    # =====================================================

    print(
        "Gemini failed. "
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
    # Groq
    # =====================================================

    print(
        "OpenRouter failed. "
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
    # Mistral
    # =====================================================

    print(
        "Groq failed. "
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
    # فشل جميع الخوادم
    # =====================================================

    return (
        "أنا Ido AI ولم أجد إجابة حاليًا."
    )


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
        return "لم يتم إرسال صورة صالحة."

    if not mime_type:
        mime_type = "image/jpeg"

    if not mime_type.startswith(
        "image/"
    ):
        return "الملف المرسل ليس صورة صالحة."

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
    # تحليل الصورة بواسطة Mistral
    # =====================================================

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
    # Groq كاحتياط
    # =====================================================

    print(
        "Mistral image failed. "
        "Trying Groq image..."
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
    # فشل تحليل الصورة
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