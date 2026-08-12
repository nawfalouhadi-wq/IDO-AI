import os
import base64
import uuid
from pathlib import Path

import requests

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

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

# مهلة Gemini للأسئلة النصية فقط: 30 ثانية
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
#
# يبقى Agent موجودًا للعمليات التي تعتمد عليه،
# لكن توليد الصور نفسه أصبح مباشرًا داخل generate_image().
#
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
        text.replace(
            "ـ",
            ""
        )
        .replace(
            "ً",
            ""
        )
        .replace(
            "ٌ",
            ""
        )
        .replace(
            "ٍ",
            ""
        )
        .replace(
            "َ",
            ""
        )
        .replace(
            "ُ",
            ""
        )
        .replace(
            "ِ",
            ""
        )
        .replace(
            "ّ",
            ""
        )
        .replace(
            "ْ",
            ""
        )
    )

    while "  " in text:

        text = text.replace(
            "  ",
            " "
        )

    return text


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
            GENERATED_IMAGE_DIR
            / filename
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

        # =====================================================
        # نبدأ بالـ output الأخير كما في توثيق Mistral
        # =====================================================

        latest_output = outputs[-1]

        latest_content = getattr(
            latest_output,
            "content",
            None
        )

        if latest_content:

            print(
                "MISTRAL LATEST OUTPUT CONTENT:",
                len(latest_content)
            )

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

                file_name = getattr(
                    chunk,
                    "file_name",
                    None
                )

                print(
                    "MISTRAL IMAGE CHUNK:",
                    index,
                    "TYPE:",
                    chunk_type,
                    "FILE_ID:",
                    file_id,
                    "FILE_NAME:",
                    file_name
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

        # =====================================================
        # احتياط: فحص باقي المخرجات
        # =====================================================

        if not file_ids:

            print(
                "MISTRAL IMAGE DEBUG: "
                "No file in latest output. "
                "Checking remaining outputs..."
            )

            for output_index, output in enumerate(
                outputs
            ):

                if output is latest_output:
                    continue

                content = getattr(
                    output,
                    "content",
                    None
                )

                if not content:
                    continue

                for index, chunk in enumerate(
                    content
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

                    print(
                        "MISTRAL FALLBACK CHUNK:",
                        "OUTPUT:",
                        output_index,
                        "INDEX:",
                        index,
                        "TYPE:",
                        chunk_type,
                        "FILE_ID:",
                        file_id
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

        # إزالة التكرار
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

        print(
            "Gemini ERROR: "
            "client غير جاهز."
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
            "Gemini ERROR:",
            e
        )

        return None


# =========================================================
# OpenRouter - نص
# =========================================================

def ask_openrouter(message):

    if not OPENROUTER_API_KEY:

        print(
            "OpenRouter ERROR: "
            "API key غير موجود."
        )

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

        answer = (
            extract_response_content(
                response.json()
            )
        )

        if answer:

            print(
                "OpenRouter response received."
            )

            return answer

        print(
            "OpenRouter returned "
            "empty response."
        )

        return None

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

        print(
            "Groq ERROR: "
            "API key غير موجود."
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

        answer = (
            extract_response_content(
                response.json()
            )
        )

        if answer:

            print(
                "Groq response received."
            )

            return answer

        print(
            "Groq returned empty response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "Groq ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Groq ERROR: "
            "connection failed."
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

        print(
            "Mistral ERROR: "
            "API key غير موجود."
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

        answer = (
            extract_response_content(
                response.json()
            )
        )

        if answer:

            print(
                "Mistral response received."
            )

            return answer

        print(
            "Mistral returned empty response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "Mistral ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Mistral ERROR: "
            "connection failed."
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

        print(
            "Trying Groq with image..."
        )

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

        print(
            "Trying Mistral with image..."
        )

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
#
# تم تغيير هذه الدالة لتستخدم Conversations API مباشرة
# مع image_generation بدل الاعتماد على Agent أثناء التوليد.
#
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

        # =====================================================
        # إنشاء الصورة مباشرة عبر Conversations API
        # =====================================================

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

        print(
            "MISTRAL IMAGE RESPONSE RECEIVED"
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

        print(
            "MISTRAL OUTPUT COUNT:",
            len(outputs)
        )

        # =====================================================
        # استخراج File IDs
        # =====================================================

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

        # =====================================================
        # تنزيل الصورة
        # =====================================================

        for file_id in file_ids:

            print(
                "MISTRAL GENERATED FILE:",
                file_id
            )

            downloaded = (
                mistral_client.files.download(
                    file_id=file_id
                )
            )

            image_bytes = (
                downloaded.read()
                if hasattr(
                    downloaded,
                    "read"
                )
                else downloaded
            )

            if not image_bytes:

                print(
                    "MISTRAL IMAGE ERROR: "
                    "Downloaded image is empty."
                )

                continue

            print(
                "MISTRAL IMAGE DOWNLOADED:",
                len(image_bytes),
                "bytes"
            )

            # =================================================
            # حفظ الصورة
            # =================================================

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

        print(
            "MISTRAL IMAGE ERROR: "
            "Could not save generated image."
        )

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

    generation_phrases = [

        # عربي
        "ولد صوره",
        "ولد لي صوره",
        "ولد لي صورة",
        "ولد صوره لي",
        "ولّد صوره",
        "ولّد لي صوره",
        "ولّد لي صورة",
        "انشئ صوره",
        "انشئ لي صوره",
        "انشئ لي صورة",
        "انشئ صوره لي",
        "انشاء صوره",
        "انشاء صوره لي",
        "انشئ صورة",
        "أنشئ صورة",
        "أنشئ لي صورة",
        "اصنع صوره",
        "اصنع لي صوره",
        "اصنع لي صورة",
        "صنع صوره",
        "ارسم صوره",
        "ارسم لي صوره",
        "ارسم لي صورة",
        "صمم صوره",
        "صمم لي صوره",
        "صمم لي صورة",
        "اعمل صوره",
        "اعمل لي صوره",
        "اعمل لي صورة",
        "سوي صوره",
        "سوي لي صوره",
        "سوي لي صورة",
        "ابغى صوره",
        "اريد صوره",
        "اريد صورة",
        "اريدك تولد صورة",
        "اريدك ان تولد صورة",
        "اريدك تصنع صورة",
        "توليد صوره",
        "توليد صورة",
        "توليد لي صورة",
        "انشاء صورة",
        "إنشاء صورة",

        # إنجليزي
        "generate an image",
        "generate image",
        "generate a picture",
        "generate picture",
        "create an image",
        "create image",
        "create a picture",
        "create picture",
        "make an image",
        "make image",
        "make a picture",
        "make picture",
        "draw an image",
        "draw image",
        "draw a picture",
        "draw picture",
        "create artwork",
        "generate artwork"
    ]

    for phrase in generation_phrases:

        normalized_phrase = (
            normalize_text(
                phrase
            )
        )

        if normalized_phrase in text:

            print(
                "IMAGE GENERATION INTENT DETECTED:",
                text
            )

            return True

    # =====================================================
    # كشف مرن إضافي
    # =====================================================

    has_image_word = any(
        word in text
        for word in (
            "صوره",
            "صورة",
            "picture",
            "image"
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

    prefixes = [

        "ولد لي صورة",
        "ولّد لي صورة",
        "ولد صورة",
        "ولّد صورة",
        "أنشئ لي صورة",
        "أنشئ صورة",
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

        "generate an image of",
        "generate image of",
        "generate a picture of",
        "create an image of",
        "create image of",
        "create a picture of",
        "make an image of",
        "make image of",
        "make a picture of",
        "draw an image of",
        "draw image of",
        "draw a picture of"
    ]

    for prefix in prefixes:

        if normalize_text(
            text
        ).startswith(
            normalize_text(
                prefix
            )
        ):

            return text[
                len(prefix):
            ].strip()

    # =====================================================
    # إزالة العبارات العامة
    # =====================================================

    cleaned = text

    cleanup_prefixes = [

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

        "generate",
        "create",
        "make",
        "draw"
    ]

    for prefix in cleanup_prefixes:

        normalized_cleaned = normalize_text(
            cleaned
        )

        normalized_prefix = normalize_text(
            prefix
        )

        if normalized_cleaned.startswith(
            normalized_prefix + " "
        ):

            cleaned = cleaned[
                len(prefix):
            ].strip()

            break

    # =====================================================
    # إزالة "صورة" / "صوره" من البداية
    # =====================================================

    for image_word in (
        "صورة",
        "صوره",
        "picture",
        "image"
    ):

        normalized_cleaned = normalize_text(
            cleaned
        )

        normalized_image_word = normalize_text(
            image_word
        )

        if normalized_cleaned.startswith(
            normalized_image_word
        ):

            cleaned = cleaned[
                len(image_word):
            ].strip()

            break

    cleaned = cleaned.strip()

    if not cleaned:
        return text

    return cleaned


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
"""


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

    print(
        "IMAGE EDIT REQUEST:",
        edit_request
    )

    # =====================================================
    # تحليل الصورة الأصلية
    # =====================================================

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

    # =====================================================
    # إنشاء Prompt جديد
    # =====================================================

    edit_prompt = (
        build_image_edit_prompt(
            image_description,
            edit_request
        )
    )

    # =====================================================
    # توليد الصورة المعدلة
    # =====================================================

    generated_image = (
        generate_image(
            edit_prompt
        )
    )

    if generated_image:

        print(
            "IMAGE EDIT COMPLETED:",
            generated_image
        )

        return generated_image

    print(
        "IMAGE EDIT FAILED."
    )

    return None


# =========================================================
# Ido AI - الرد الرئيسي
# =========================================================

def get_response(
    message
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

    message_lower = normalize_text(
        original_message
    )

    # =====================================================
    # إنشاء صورة من الصفر
    # يجب أن يكون هذا قبل أي نموذج نصي
    # =====================================================

    if is_image_generation_request(
        original_message
    ):

        print(
            "DIRECT IMAGE GENERATION REQUEST:",
            original_message
        )

        image_prompt = (
            get_image_prompt(
                original_message
            )
        )

        if not image_prompt:

            image_prompt = (
                original_message
            )

        generated = (
            generate_image(
                image_prompt
            )
        )

        if generated:

            return (
                "IMAGE_URL:"
                f"{generated}"
            )

        return (
            "تعذر إنشاء الصورة حاليًا. "
            "تحقق من أن Mistral Image Generation "
            "يعمل بشكل صحيح."
        )

    # =====================================================
    # الردود السريعة والثابتة
    # =====================================================

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

        "شكراً":
            "العفو، يسعدني مساعدتك.",

        "وداعا":
            "إلى اللقاء! أتمنى لك يومًا سعيدًا."
    }

    for key, value in responses.items():

        if normalize_text(
            key
        ) in message_lower:

            return value

    # =====================================================
    # Gemini أولًا
    # Gemini للأسئلة النصية فقط
    # =====================================================

    answer = ask_gemini(
        original_message
    )

    if answer:

        return answer

    # =====================================================
    # OpenRouter ثانيًا
    # =====================================================

    print(
        "Gemini failed. "
        "Trying OpenRouter..."
    )

    answer = ask_openrouter(
        original_message
    )

    if answer:

        return answer

    # =====================================================
    # Groq ثالثًا
    # =====================================================

    print(
        "OpenRouter failed. "
        "Trying Groq..."
    )

    answer = ask_groq(
        original_message
    )

    if answer:

        return answer

    # =====================================================
    # Mistral رابعًا
    # =====================================================

    print(
        "Groq failed. "
        "Trying Mistral..."
    )

    answer = ask_mistral(
        original_message
    )

    if answer:

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

    # =====================================================
    # طلب تعديل الصورة
    # =====================================================

    if is_image_edit_request(
        message
    ):

        generated_image = (
            edit_image(
                message,
                image_bytes,
                mime_type
            )
        )

        if generated_image:

            return (
                "IMAGE_URL:"
                f"{generated_image}"
            )

        return (
            "تعذر تعديل الصورة حاليًا."
        )

    # =====================================================
    # تحليل الصورة بـ Mistral
    # =====================================================

    answer = ask_mistral_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:

        return answer

    # =====================================================
    # Groq كاحتياط فقط لتحليل الصورة
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

        return answer

    # =====================================================
    # فشل جميع خوادم تحليل الصور
    # =====================================================

    return (
        "تعذر تحليل الصورة حاليًا."
    )