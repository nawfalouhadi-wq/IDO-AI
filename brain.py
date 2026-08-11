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
except Exception:
    Mistral = None

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

gemini_client = None

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=HttpOptions(
                timeout=10000
            )
        )

        print(
            "GEMINI CLIENT: READY"
        )

        print(
            "GEMINI MODEL:",
            GEMINI_MODEL
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
# Image Generation Agent
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
                    "Generate high-quality images "
                    "from the user's description. "
                    "When the user asks to modify "
                    "a described object, recreate "
                    "the scene while applying the "
                    "requested modification."
                ),
                tools=[
                    {
                        "type":
                            "image_generation"
                    }
                ],
                completion_args={
                    "temperature":
                        0.3,
                    "top_p":
                        0.95
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
# استخراج محتوى الاستجابة
# =========================================================

def extract_response_content(
    data
):

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

    message_data = (
        choices[0].get(
            "message",
            {}
        )
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
# استخراج ملفات الصور من استجابة Mistral
# =========================================================

def extract_generated_images(
    response
):

    images = []

    if response is None:
        return images

    outputs = getattr(
        response,
        "outputs",
        None
    )

    if not outputs:
        return images

    for output in outputs:

        content = getattr(
            output,
            "content",
            None
        )

        if not content:
            continue

        for chunk in content:

            file_id = getattr(
                chunk,
                "file_id",
                None
            )

            chunk_type = getattr(
                chunk,
                "type",
                None
            )

            if not file_id:
                continue

            if (
                chunk_type not in
                (
                    "tool_file",
                    "file"
                )
            ):
                continue

            images.append(
                file_id
            )

    return images


# =========================================================
# Gemini - نص
# =========================================================

def ask_gemini(
    message
):

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

def ask_openrouter(
    message
):

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

            timeout=REQUEST_TIMEOUT
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

        data = response.json()

        answer = (
            extract_response_content(
                data
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

def ask_groq(
    message
):

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

        data = response.json()

        answer = (
            extract_response_content(
                data
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

def ask_mistral(
    message
):

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

        data = response.json()

        answer = (
            extract_response_content(
                data
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

        print(
            "Groq IMAGE ERROR: "
            "API key غير موجود."
        )

        return None

    if not image_bytes:

        print(
            "Groq IMAGE ERROR: "
            "الصورة فارغة."
        )

        return None

    try:

        print(
            "Trying Groq with image..."
        )

        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode("utf-8")
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

        data = response.json()

        answer = (
            extract_response_content(
                data
            )
        )

        if answer:

            print(
                "Groq image response received."
            )

            return answer

        print(
            "Groq returned empty "
            "image response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "Groq IMAGE ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Groq IMAGE ERROR: "
            "connection failed."
        )

        return None

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

        print(
            "Mistral IMAGE ERROR: "
            "API key غير موجود."
        )

        return None

    if not image_bytes:

        print(
            "Mistral IMAGE ERROR: "
            "الصورة فارغة."
        )

        return None

    try:

        print(
            "Trying Mistral with image..."
        )

        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode("utf-8")
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

        data = response.json()

        answer = (
            extract_response_content(
                data
            )
        )

        if answer:

            print(
                "Mistral image response "
                "received."
            )

            return answer

        print(
            "Mistral returned empty "
            "image response."
        )

        return None

    except requests.exceptions.Timeout:

        print(
            "Mistral IMAGE ERROR: timeout."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Mistral IMAGE ERROR: "
            "connection failed."
        )

        return None

    except Exception as e:

        print(
            "Mistral IMAGE ERROR:",
            e
        )

        return None


# =========================================================
# Mistral - توليد صورة
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

    if mistral_client is None:

        print(
            "IMAGE GENERATION ERROR: "
            "Mistral client غير جاهز."
        )

        return None

    if mistral_image_agent is None:

        print(
            "IMAGE GENERATION ERROR: "
            "Mistral image agent غير جاهز."
        )

        return None

    try:

        print(
            "Trying Mistral image generation..."
        )

        response = (
            mistral_client.beta.conversations.start(
                agent_id=(
                    mistral_image_agent.id
                ),
                inputs=prompt
            )
        )

        file_ids = (
            extract_generated_images(
                response
            )
        )

        if not file_ids:

            print(
                "Mistral image generation "
                "returned no image file."
            )

            return None

        file_id = file_ids[0]

        print(
            "Mistral generated file:",
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

        image_url = (
            save_generated_image(
                image_bytes
            )
        )

        if image_url:

            print(
                "Generated image saved:",
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
# التحقق من طلب إنشاء صورة
# =========================================================

def is_image_generation_request(
    message
):

    if not message:
        return False

    text = str(
        message
    ).strip().lower()

    image_words = [

        "أنشئ صورة",
        "انشئ صورة",
        "اصنع صورة",
        "صنع صورة",
        "إنشاء صورة",
        "انشاء صورة",
        "ولد صورة",
        "ولّد صورة",
        "ارسم صورة",
        "ارسم لي",
        "صورة لي",

        "generate an image",
        "generate image",
        "create an image",
        "create image",
        "make an image",
        "make image",
        "draw an image",
        "draw image"
    ]

    for word in image_words:

        if word in text:
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

        "أنشئ لي صورة",
        "أنشئ صورة",
        "انشئ لي صورة",
        "انشئ صورة",
        "اصنع لي صورة",
        "اصنع صورة",
        "إنشاء صورة",
        "انشاء صورة",
        "ارسم لي",
        "ارسم صورة",

        "generate an image of",
        "generate image of",
        "create an image of",
        "create image of",
        "make an image of",
        "make image of"
    ]

    for prefix in prefixes:

        if text.lower().startswith(
            prefix.lower()
        ):

            return text[
                len(prefix):
            ].strip()

    return text


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

    message_lower = (
        original_message.lower()
    )


    # =====================================================
    # طلب إنشاء صورة
    # =====================================================

    if is_image_generation_request(
        original_message
    ):

        image_prompt = (
            get_image_prompt(
                original_message
            )
        )

        if not image_prompt:

            return (
                "اكتب لي وصف الصورة "
                "التي تريد إنشاءها."
            )

        generated = generate_image(
            image_prompt
        )

        if generated:

            return (
                "تم إنشاء الصورة:\n"
                f"{generated}"
            )

        return (
            "تعذر إنشاء الصورة حاليًا."
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

        "من انشاك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من أنشأك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صممك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صاحبك":
            "أنا Ido AI، وقد تم تطويري "
            "وبنائي بواسطة Noufal Ouhadi.",

        "من وراءك":
            "تم تطويري وبنائي بواسطة "
            "Noufal Ouhadi، وأنا Ido AI.",

        "من صنع ido ai":
            "تم تطوير Ido AI وبناؤه "
            "بواسطة Noufal Ouhadi.",

        "من طور ido ai":
            "تم تطوير Ido AI بواسطة "
            "Noufal Ouhadi.",

        "الوقت":
            "يمكنك معرفة الوقت من النظام.",

        "كم عدد الناس في العالم":
            "يبلغ عدد سكان العالم "
            "أكثر من 8 مليارات نسمة.",

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


    # =====================================================
    # البحث في الردود الجاهزة
    # =====================================================

    for key, value in responses.items():

        if key in message_lower:

            return value


    # =====================================================
    # Gemini أولًا
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
# تحليل صورة
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
    # Mistral مع الصورة أولًا
    # =====================================================

    answer = ask_mistral_image(
        message,
        image_bytes,
        mime_type
    )

    if answer:

        return answer


    # =====================================================
    # Groq مع الصورة ثانيًا
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