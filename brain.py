# ============================================================
# Ido AI - APPEND-ONLY INTELLIGENCE LAYER
# ============================================================
#
# IMPORTANT:
# ------------------------------------------------------------
# هذا القسم مضاف فقط.
#
# لا نحذف أي شيء من brain.py الأصلي.
# لا نغير الدوال القديمة.
#
# Python سيستخدم التعريفات الجديدة الموجودة في نهاية الملف
# عند استدعاء الدوال بعد تحميل الملف.
#
# الهدف:
#
# 1. تحسين Failover
# 2. اكتشاف موديلات Groq Vision المتاحة تلقائيًا
# 3. منع توقف النظام بسبب موديل Vision قديم أو غير متاح
# 4. إضافة طبقة موحدة للتعامل مع النص والصورة
# 5. الحفاظ على جميع الدوال القديمة
# 6. عدم الاعتماد على Gemini كمحرك للصورة
# 7. عدم حذف أي Provider موجود مسبقًا
#
# ============================================================

import json
import re
from typing import Any, Optional


# ============================================================
# ADVANCED SETTINGS
# ============================================================

ADVANCED_FAILOVER_ENABLED = (
    os.getenv(
        "ADVANCED_FAILOVER_ENABLED",
        "true"
    ).lower() == "true"
)

ADVANCED_MODEL_DISCOVERY = (
    os.getenv(
        "ADVANCED_MODEL_DISCOVERY",
        "true"
    ).lower() == "true"
)

ADVANCED_MAX_PROVIDER_ATTEMPTS = int(
    os.getenv(
        "ADVANCED_MAX_PROVIDER_ATTEMPTS",
        "6"
    )
)

ADVANCED_RETRY_DELAY = float(
    os.getenv(
        "ADVANCED_RETRY_DELAY",
        "0.25"
    )
)


# ============================================================
# PROVIDER STATISTICS
# ============================================================

_PROVIDER_STATS = {}


def _provider_stat(
    provider,
    success=False,
    failure=False
):
    """
    يحفظ إحصائيات بسيطة لكل Provider.

    لا يؤثر على النظام القديم.
    """

    if provider not in _PROVIDER_STATS:

        _PROVIDER_STATS[provider] = {
            "success": 0,
            "failure": 0,
            "attempts": 0
        }

    _PROVIDER_STATS[
        provider
    ]["attempts"] += 1

    if success:

        _PROVIDER_STATS[
            provider
        ]["success"] += 1

    if failure:

        _PROVIDER_STATS[
            provider
        ]["failure"] += 1


def get_provider_stats():

    return dict(
        _PROVIDER_STATS
    )


# ============================================================
# ADVANCED FAILURE CLASSIFICATION
# ============================================================

def _is_retryable_status(
    status_code
):

    return status_code in (
        408,
        409,
        425,
        429,
        500,
        502,
        503,
        504,
    )


def _is_provider_error(
    error_text
):

    if not error_text:

        return False

    text = str(
        error_text
    ).lower()

    error_words = [

        "timeout",
        "timed out",

        "connection",
        "connection refused",

        "temporarily unavailable",

        "rate limit",
        "rate_limit",

        "quota",

        "overloaded",

        "server error",

        "internal server error",

        "model not found",

        "does not exist",

        "not available",

        "no access",

        "unsupported",

        "invalid model"
    ]

    return any(
        word in text
        for word in error_words
    )


# ============================================================
# SAFE JSON REQUEST
# ============================================================

def _safe_post_json(
    provider,
    url,
    headers=None,
    payload=None,
    timeout=None
):

    if timeout is None:

        timeout = REQUEST_TIMEOUT

    try:

        response = requests.post(

            url,

            headers=headers or {},

            json=payload or {},

            timeout=timeout
        )

        print(
            f"{provider} HTTP STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                f"{provider} HTTP ERROR:",
                response.text[:2000]
            )

            return None, response.status_code

        data = request_json(
            response,
            provider
        )

        if not data:

            return None, response.status_code

        return data, response.status_code

    except Exception as exc:

        print(
            f"{provider} REQUEST ERROR:",
            exc
        )

        return None, None


# ============================================================
# GROQ MODEL DISCOVERY
# ============================================================
#
# المشكلة التي ظهرت عندك كانت:
#
# meta-llama/llama-4-scout-17b-16e-instruct
#
# 404 / model_not_found
#
# لذلك لا نعتمد على هذا الاسم فقط.
#
# نحاول معرفة الموديلات الموجودة فعليًا في حساب Groq.
#
# ============================================================

_GROQ_DISCOVERED_MODELS = None
_GROQ_DISCOVERY_TIME = 0

GROQ_DISCOVERY_CACHE_SECONDS = int(
    os.getenv(
        "GROQ_DISCOVERY_CACHE_SECONDS",
        "600"
    )
)


def discover_groq_models(
    force=False
):

    global _GROQ_DISCOVERED_MODELS
    global _GROQ_DISCOVERY_TIME

    if not GROQ_API_KEY:

        return []

    now = time.time()

    if (
        not force
        and
        _GROQ_DISCOVERED_MODELS is not None
        and
        now - _GROQ_DISCOVERY_TIME
        < GROQ_DISCOVERY_CACHE_SECONDS
    ):

        return _GROQ_DISCOVERED_MODELS

    url = (
        "https://api.groq.com/openai/v1/models"
    )

    headers = {

        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json"
    }

    try:

        print(
            "GROQ MODEL DISCOVERY: STARTED"
        )

        response = requests.get(

            url,

            headers=headers,

            timeout=REQUEST_TIMEOUT
        )

        print(
            "GROQ MODEL DISCOVERY STATUS:",
            response.status_code
        )

        if response.status_code != 200:

            print(
                "GROQ MODEL DISCOVERY RESPONSE:",
                response.text[:1500]
            )

            return []

        data = response.json()

        models = data.get(
            "data",
            []
        )

        result = []

        for item in models:

            if not isinstance(
                item,
                dict
            ):

                continue

            model_id = item.get(
                "id"
            )

            if model_id:

                result.append(
                    str(model_id)
                )

        _GROQ_DISCOVERED_MODELS = result

        _GROQ_DISCOVERY_TIME = now

        print(
            "GROQ DISCOVERED MODELS:",
            len(result)
        )

        return result

    except Exception as exc:

        print(
            "GROQ MODEL DISCOVERY ERROR:",
            exc
        )

        return []


# ============================================================
# GROQ VISION MODEL SELECTION
# ============================================================

def _looks_like_vision_model(
    model_id
):

    if not model_id:

        return False

    text = str(
        model_id
    ).lower()

    vision_keywords = [

        "vision",
        "vl",
        "multimodal",
        "qwen",
        "gemma"
    ]

    return any(
        word in text
        for word in vision_keywords
    )


def get_groq_vision_models():

    candidates = []

    # --------------------------------------------------------
    # 1. User-defined model
    # --------------------------------------------------------

    configured = os.getenv(
        "GROQ_VISION_MODEL",
        ""
    ).strip()

    if configured:

        candidates.append(
            configured
        )

    # --------------------------------------------------------
    # 2. Current Groq model list
    # --------------------------------------------------------

    if ADVANCED_MODEL_DISCOVERY:

        discovered = discover_groq_models()

        for model in discovered:

            if _looks_like_vision_model(
                model
            ):

                if model not in candidates:

                    candidates.append(
                        model
                    )

    # --------------------------------------------------------
    # 3. Known/current candidates
    # --------------------------------------------------------

    known_candidates = [

        "qwen/qwen3.6-27b",

        "meta-llama/llama-4-scout-17b-16e-instruct",

        "meta-llama/llama-4-scout-17b-16e",

        "meta-llama/llama-4-maverick-17b-128e-instruct"
    ]

    for model in known_candidates:

        if model not in candidates:

            candidates.append(
                model
            )

    return candidates


# ============================================================
# ADVANCED GROQ VISION
# ============================================================

def ask_groq_image_advanced(
    message,
    image_bytes,
    mime_type
):

    if not GROQ_API_KEY:

        return None

    if not image_bytes:

        return None

    if not provider_available(
        "GROQ_VISION_ADVANCED"
    ):

        return None

    image_url = image_to_data_url(
        image_bytes,
        mime_type
    )

    if not image_url:

        return None

    models = get_groq_vision_models()

    if not models:

        print(
            "GROQ VISION: "
            "No candidate models discovered."
        )

        return None

    print(
        "GROQ VISION CANDIDATES:",
        models
    )

    for model in models:

        try:

            print(
                "Trying Groq Vision Model:",
                model
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
                        model,

                    "messages": [

                        {

                            "role":
                                "system",

                            "content":
                                (
                                    "You are Ido AI. "
                                    "Analyze the provided image "
                                    "carefully. "
                                    "Answer in the user's language."
                                )
                        },

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
                                            image_url
                                    }
                                }
                            ]
                        }
                    ],

                    "temperature":
                        0.3,

                    "max_completion_tokens":
                        4096
                },

                timeout=REQUEST_TIMEOUT
            )

            print(
                "Groq Vision Model Status:",
                response.status_code,
                model
            )

            if response.status_code != 200:

                print(
                    "Groq Vision Model Error:",
                    response.text[:1500]
                )

                # ------------------------------------------------
                # إذا كان الموديل غير موجود:
                # انتقل مباشرة إلى موديل آخر.
                # ------------------------------------------------

                if response.status_code == 404:

                    continue

                if _is_retryable_status(
                    response.status_code
                ):

                    continue

                continue

            data = request_json(
                response,
                "Groq Vision Advanced"
            )

            if not data:

                continue

            answer = extract_text_from_response(
                data
            )

            if answer:

                _provider_stat(
                    "GROQ_VISION",
                    success=True
                )

                print(
                    "GROQ VISION ADVANCED: SUCCESS"
                )

                print(
                    "GROQ VISION MODEL USED:",
                    model
                )

                return answer

        except Exception as exc:

            _provider_stat(
                "GROQ_VISION",
                failure=True
            )

            print(
                "Groq Vision Advanced ERROR:",
                exc
            )

            continue

    print(
        "GROQ VISION ADVANCED: ALL MODELS FAILED"
    )

    return None


# ============================================================
# GENERIC IMAGE DATA EXTRACTION
# ============================================================

def _extract_image_deep(
    data
):

    if not data:

        return None

    # --------------------------------------------------------
    # Existing extractor first
    # --------------------------------------------------------

    image = extract_image_from_response(
        data
    )

    if image:

        return image

    # --------------------------------------------------------
    # Recursive search
    # --------------------------------------------------------

    def walk(
        value
    ):

        if isinstance(
            value,
            dict
        ):

            for key, item in value.items():

                key_lower = str(
                    key
                ).lower()

                if key_lower in (
                    "url",
                    "image_url",
                    "imageurl"
                ):

                    if isinstance(
                        item,
                        str
                    ):

                        if (
                            item.startswith(
                                "http://"
                            )
                            or
                            item.startswith(
                                "https://"
                            )
                            or
                            item.startswith(
                                "data:image/"
                            )
                        ):

                            return item

                    if isinstance(
                        item,
                        dict
                    ):

                        nested_url = (
                            item.get("url")
                            or
                            item.get("uri")
                        )

                        if nested_url:

                            return nested_url

                if key_lower in (
                    "b64_json",
                    "base64",
                    "data"
                ):

                    if isinstance(
                        item,
                        str
                    ):

                        # لا نعتبر النص العادي صورة.
                        if len(item) > 500:

                            if not item.startswith(
                                "http"
                            ):

                                return (
                                    "data:image/png;base64,"
                                    + item
                                )

                result = walk(
                    item
                )

                if result:

                    return result

        elif isinstance(
            value,
            list
        ):

            for item in value:

                result = walk(
                    item
                )

                if result:

                    return result

        return None

    return walk(
        data
    )


# ============================================================
# IMAGE GENERATION PROVIDER CHAIN
# ============================================================
#
# هذه الطبقة لا تحذف generate_image القديمة.
#
# بل تضيف Router جديدًا.
#
# ============================================================

def _advanced_generate_image_chain(
    prompt
):

    prompt = clean_answer(
        prompt
    )

    if not prompt:

        return {

            "answer":
                "اكتب وصف الصورة التي تريد إنشاءها.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)

    print(
        "ADVANCED IMAGE GENERATION ROUTER"
    )

    print(
        "PROMPT:",
        prompt
    )

    print("=" * 60)

    # --------------------------------------------------------
    # 1. Existing xAI generator
    # --------------------------------------------------------

    try:

        image = generate_image_xai(
            prompt
        )

        if image:

            return {

                "answer":
                    "تم إنشاء الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "xAI"
            }

    except Exception as exc:

        print(
            "ADVANCED xAI IMAGE ERROR:",
            exc
        )

    # --------------------------------------------------------
    # 2. Existing OpenRouter generator
    # --------------------------------------------------------

    try:

        image = generate_image_openrouter(
            prompt
        )

        if image:

            return {

                "answer":
                    "تم إنشاء الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "OpenRouter"
            }

    except Exception as exc:

        print(
            "ADVANCED OPENROUTER IMAGE ERROR:",
            exc
        )

    # --------------------------------------------------------
    # 3. Existing Pollinations generator
    # --------------------------------------------------------

    try:

        image = generate_image_pollinations(
            prompt
        )

        if image:

            return {

                "answer":
                    "تم إنشاء الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "Pollinations"
            }

    except Exception as exc:

        print(
            "ADVANCED POLLINATIONS IMAGE ERROR:",
            exc
        )

    print(
        "ADVANCED IMAGE GENERATION: "
        "ALL PROVIDERS FAILED"
    )

    return {

        "answer":
            "تعذر إنشاء الصورة حاليًا. "
            "تمت تجربة جميع مولدات الصور "
            "المتاحة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# ADVANCED IMAGE EDITING CHAIN
# ============================================================

def _advanced_edit_image_chain(
    prompt,
    image_bytes,
    mime_type
):

    if not image_bytes:

        return {

            "answer":
                "لم يتم إرسال صورة صالحة.",

            "imageUrl":
                "",

            "provider":
                None
        }

    print("=" * 60)

    print(
        "ADVANCED IMAGE EDITING ROUTER"
    )

    print(
        "PROMPT:",
        prompt
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes)
    )

    print("=" * 60)

    # --------------------------------------------------------
    # 1. xAI
    # --------------------------------------------------------

    try:

        image = edit_image_xai(

            prompt,

            image_bytes,

            mime_type
        )

        if image:

            return {

                "answer":
                    "تم تعديل الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "xAI"
            }

    except Exception as exc:

        print(
            "ADVANCED xAI EDIT ERROR:",
            exc
        )

    # --------------------------------------------------------
    # 2. OpenRouter
    # --------------------------------------------------------

    try:

        image = edit_image_openrouter(

            prompt,

            image_bytes,

            mime_type
        )

        if image:

            return {

                "answer":
                    "تم تعديل الصورة بنجاح.",

                "imageUrl":
                    image,

                "provider":
                    "OpenRouter"
            }

    except Exception as exc:

        print(
            "ADVANCED OPENROUTER EDIT ERROR:",
            exc
        )

    print(
        "ADVANCED IMAGE EDITING: "
        "ALL PROVIDERS FAILED"
    )

    return {

        "answer":
            "تعذر تعديل الصورة حاليًا. "
            "تمت تجربة خدمات تعديل الصور "
            "المتاحة.",

        "imageUrl":
            "",

        "provider":
            None
    }


# ============================================================
# ADVANCED VISION ROUTER
# ============================================================

def _advanced_vision_chain(
    message,
    image_bytes,
    mime_type
):

    routes = [

        (
            "MISTRAL_VISION",
            ask_mistral_image
        ),

        (
            "GROQ_VISION_ADVANCED",
            ask_groq_image_advanced
        ),

        (
            "OPENROUTER_VISION",
            ask_openrouter_image
        ),

        (
            "XAI_VISION",
            ask_xai_image
        )
    ]

    attempts = 0

    for name, function in routes:

        if attempts >= (
            ADVANCED_MAX_PROVIDER_ATTEMPTS
        ):

            break

        attempts += 1

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(cooldown)"
            )

            continue

        print("=" * 40)

        print(
            "ADVANCED VISION TRY:",
            name
        )

        print("=" * 40)

        try:

            if name == (
                "GROQ_VISION_ADVANCED"
            ):

                answer = function(

                    message,

                    image_bytes,

                    mime_type
                )

            else:

                answer = function(

                    message,

                    image_bytes,

                    mime_type
                )

        except Exception as exc:

            _provider_stat(
                name,
                failure=True
            )

            print(
                f"{name} ERROR:",
                exc
            )

            answer = None

        if answer:

            _provider_stat(
                name,
                success=True
            )

            print(
                "ADVANCED VISION SUCCESS:",
                name
            )

            return answer

        print(
            f"{name} failed."
        )

        if ADVANCED_RETRY_DELAY > 0:

            time.sleep(
                ADVANCED_RETRY_DELAY
            )

    return None


# ============================================================
# SMART IMAGE INTENT DETECTION
# ============================================================

def _contains_any(
    text,
    words
):

    if not text:

        return False

    normalized = str(
        text
    ).lower().strip()

    return any(
        str(word).lower() in normalized
        for word in words
    )


def _smart_is_edit_request(
    message,
    has_image=True
):

    if not has_image:

        return False

    edit_words = [

        "عدل",
        "عدّل",

        "تعديل",

        "غيّر",
        "غير",

        "غير لون",
        "غيّر لون",

        "بدل",
        "بدّل",

        "استبدل",

        "احذف من الصورة",
        "أضف إلى الصورة",

        "أضف للصورة",
        "اضف للصورة",

        "remove",
        "edit",
        "modify",
        "change",
        "replace",

        "make the car",
        "make it blue",
        "make it red"
    ]

    return _contains_any(
        message,
        edit_words
    )


# ============================================================
# SMART IMAGE GENERATION DETECTION
# ============================================================

def _smart_is_generation_request(
    message
):

    words = [

        "أنشئ صورة",
        "انشئ صورة",

        "أنشئ لي صورة",
        "انشئ لي صورة",

        "اصنع صورة",
        "اصنع لي صورة",

        "ارسم صورة",
        "ارسم لي",

        "صمم صورة",
        "صمم لي",

        "ولد صورة",
        "ولّد صورة",

        "generate image",
        "generate an image",

        "create image",
        "create an image",

        "make image",
        "make an image",

        "draw image",
        "draw an image",

        "create a picture",
        "generate a picture"
    ]

    return _contains_any(
        message,
        words
    )


# ============================================================
# SMART IMAGE PROMPT
# ============================================================

def _advanced_image_prompt(
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

        "ارسم لي",
        "ارسم صورة",

        "صمم لي صورة",
        "صمم صورة",

        "ولد صورة",
        "ولّد صورة",

        "generate an image of",
        "generate an image",

        "generate image of",
        "generate image",

        "create an image of",
        "create an image",

        "create image of",
        "create image",

        "make an image of",
        "make an image",

        "make image of",
        "make image",

        "draw an image of",
        "draw an image",

        "create a picture of",
        "create a picture",

        "generate a picture of",
        "generate a picture"
    ]

    lower = text.lower()

    for prefix in prefixes:

        if lower.startswith(
            prefix.lower()
        ):

            return text[
                len(prefix):
            ].strip()

    return text


# ============================================================
# OVERRIDE generate_image
# ============================================================
#
# لا نحذف generate_image القديمة.
# هذا تعريف جديد في نهاية الملف.
#
# ============================================================

def generate_image(
    prompt
):

    if not ADVANCED_FAILOVER_ENABLED:

        return _advanced_generate_image_chain(
            prompt
        )

    return _advanced_generate_image_chain(
        prompt
    )


# ============================================================
# OVERRIDE get_image_response
# ============================================================
#
# هذا هو أهم جزء.
#
# لا نحذف get_image_response القديمة.
#
# التعريف الجديد يأتي في نهاية الملف ولذلك Python سيستخدمه.
#
# ============================================================

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

    if not message:

        message = (
            "حلل هذه الصورة واشرح لي "
            "ما الذي يظهر فيها."
        )

    message = str(
        message
    ).strip()

    print("=" * 60)

    print(
        "ADVANCED IMAGE ROUTER STARTED"
    )

    print(
        "IMAGE MIME TYPE:",
        mime_type
    )

    print(
        "IMAGE SIZE:",
        len(image_bytes),
        "bytes"
    )

    print(
        "IMAGE QUESTION:",
        message
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print("=" * 60)

    # ========================================================
    # 1. IMAGE EDIT
    # ========================================================

    if _smart_is_edit_request(
        message,
        has_image=True
    ):

        print(
            "ADVANCED REQUEST TYPE: IMAGE EDIT"
        )

        result = _advanced_edit_image_chain(

            message,

            image_bytes,

            mime_type
        )

        if result.get(
            "imageUrl"
        ):

            return result

        # ----------------------------------------------------
        # إذا فشل التعديل:
        # لا نرجع مباشرة بخطأ.
        #
        # نحاول أولاً تحليل الصورة.
        # ----------------------------------------------------

        print(
            "IMAGE EDIT FAILED."
        )

        print(
            "FALLBACK: IMAGE UNDERSTANDING"
        )

    # ========================================================
    # 2. IMAGE UNDERSTANDING
    # ========================================================

    print(
        "ADVANCED REQUEST TYPE: "
        "IMAGE UNDERSTANDING"
    )

    answer = _advanced_vision_chain(

        message,

        image_bytes,

        mime_type
    )

    if answer:

        return answer

    # ========================================================
    # 3. FINAL FAILURE
    # ========================================================

    return (
        "تعذر تحليل الصورة حاليًا. "
        "تمت تجربة مزودي الرؤية المتاحين "
        "واختيار موديلات بديلة عند الحاجة، "
        "ولكن لم يُرجع أي مزود نتيجة صالحة."
    )


# ============================================================
# OVERRIDE get_response
# ============================================================
#
# نحافظ على get_response الأصلية أيضًا.
#
# التعريف الجديد:
# - يكتشف إنشاء الصور
# - ثم يمرر النص إلى سلسلة الذكاء الاصطناعي
# - لا يزيل أي Provider
#
# ============================================================

def get_response(
    message,
    conversation_id=None
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

    if _smart_is_generation_request(
        original_message
    ):

        prompt = _advanced_image_prompt(
            original_message
        )

        if prompt:

            print(
                "ADVANCED TEXT -> IMAGE REQUEST"
            )

            return _advanced_generate_image_chain(
                prompt
            )

    # ========================================================
    # QUICK RESPONSES
    # ========================================================

    quick = quick_response(
        original_message
    )

    if quick:

        return quick

    # ========================================================
    # TEXT FAILOVER
    # ========================================================

    routes = [

        (
            "GROQ",
            ask_groq
        ),

        (
            "MISTRAL",
            ask_mistral
        ),

        (
            "OPENROUTER",
            ask_openrouter
        ),

        (
            "GEMINI",
            ask_gemini
        ),

        (
            "XAI",
            ask_xai
        ),

        (
            "POLLINATIONS",
            ask_pollinations
        )
    ]

    attempts = 0

    for name, function in routes:

        if attempts >= (
            ADVANCED_MAX_PROVIDER_ATTEMPTS
        ):

            print(
                "Maximum provider attempts reached."
            )

            break

        attempts += 1

        if not provider_available(
            name
        ):

            print(
                f"{name}: SKIPPED "
                "(cooldown)"
            )

            continue

        print("=" * 40)

        print(
            "ADVANCED TEXT TRY:",
            name
        )

        print("=" * 40)

        try:

            answer = function(
                original_message
            )

        except Exception as exc:

            _provider_stat(
                name,
                failure=True
            )

            print(
                f"{name} ROUTER ERROR:",
                exc
            )

            answer = None

        if answer:

            _provider_stat(
                name,
                success=True
            )

            print(
                "TEXT ROUTE SUCCESS:",
                name
            )

            return answer

        print(
            f"{name} failed. "
            "Trying next provider..."
        )

        if ADVANCED_RETRY_DELAY > 0:

            time.sleep(
                ADVANCED_RETRY_DELAY
            )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return (
        "أنا Ido AI، لكن جميع مزودي "
        "الذكاء الاصطناعي المتاحين "
        "فشلوا حاليًا. "
        "تحقق من المفاتيح والرصيد "
        "وحالة مزودي الخدمة."
    )


# ============================================================
# CAPABILITY INFORMATION
# ============================================================

def get_ai_capabilities():

    return {

        "text": [

            "GROQ",
            "MISTRAL",
            "OPENROUTER",
            "GEMINI",
            "XAI",
            "POLLINATIONS"
        ],

        "vision": [

            "MISTRAL",
            "GROQ",
            "OPENROUTER",
            "XAI"
        ],

        "image_generation": [

            "XAI",
            "OPENROUTER",
            "POLLINATIONS"
        ],

        "image_editing": [

            "XAI",
            "OPENROUTER"
        ],

        "automatic_failover":
            True,

        "groq_model_discovery":
            ADVANCED_MODEL_DISCOVERY
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def get_brain_status():

    status = {

        "brain":
            "online",

        "advanced_router":
            ADVANCED_FAILOVER_ENABLED,

        "providers": {}
    }

    provider_keys = {

        "GROQ":
            bool(GROQ_API_KEY),

        "MISTRAL":
            bool(MISTRAL_API_KEY),

        "OPENROUTER":
            bool(OPENROUTER_API_KEY),

        "GEMINI":
            bool(GEMINI_API_KEY),

        "XAI":
            bool(XAI_API_KEY),

        "POLLINATIONS":
            bool(POLLINATIONS_API_KEY)
    }

    for name, enabled in (
        provider_keys.items()
    ):

        status["providers"][
            name
        ] = {

            "configured":
                enabled,

            "available":
                (
                    enabled
                    and
                    provider_available(
                        name
                    )
                )
        }

    return status


# ============================================================
# STARTUP - ADVANCED LAYER
# ============================================================

print("=" * 60)

print(
    "IDO AI ADVANCED FAILOVER LAYER: READY"
)

print(
    "APPEND-ONLY MODE: ENABLED"
)

print(
    "TEXT FAILOVER:"
)

print(
    "GROQ -> MISTRAL -> OPENROUTER -> "
    "GEMINI -> XAI -> POLLINATIONS"
)

print(
    "VISION FAILOVER:"
)

print(
    "MISTRAL -> GROQ(AUTO MODEL) -> "
    "OPENROUTER -> XAI"
)

print(
    "IMAGE GENERATION FAILOVER:"
)

print(
    "xAI -> OPENROUTER -> POLLINATIONS"
)

print(
    "IMAGE EDITING FAILOVER:"
)

print(
    "xAI -> OPENROUTER"
)

print(
    "GROQ MODEL AUTO-DISCOVERY:",
    ADVANCED_MODEL_DISCOVERY
)

print(
    "MAX PROVIDER ATTEMPTS:",
    ADVANCED_MAX_PROVIDER_ATTEMPTS
)

print("=" * 60)