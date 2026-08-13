# ============================================================
# IDO AI - APP.PY
# ============================================================
#
# PROVIDER ROUTING
#
# TEXT:
#     GROQ
#       ↓
#     OPENROUTER
#       ↓
#     GEMINI
#
# IMAGES:
#     MISTRAL ONLY
#
#     - Image analysis
#     - Image generation
#     - Image editing
#
# API.PY:
#     TEXT API ONLY
#
# ============================================================

from flask import (
    Flask,
    render_template,
    request
)

from datetime import datetime

import os


# ============================================================
# BRAIN
# ============================================================

from brain import (
    get_response,
    get_image_response
)


# ============================================================
# OTHER MODULES
# ============================================================

from calculator import calculate
from translator import translate

from memory import (
    get_answer,
    create_conversation
)


# ============================================================
# API
# ============================================================

try:

    from api import api

    api_available = True

except Exception as e:

    print(
        "API IMPORT ERROR:",
        repr(e)
    )

    api_available = False


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder="templates"
)


# ============================================================
# REGISTER API BLUEPRINT
# ============================================================

if api_available:

    try:

        app.register_blueprint(
            api
        )

        print(
            "API BLUEPRINT: REGISTERED"
        )

    except Exception as e:

        print(
            "API REGISTER ERROR:",
            repr(e)
        )

        api_available = False

else:

    print(
        "API BLUEPRINT: DISABLED"
    )


# ============================================================
# CONVERSATION ID
# ============================================================

def resolve_conversation_id(
    conversation_id=None
):
    """
    Return the current conversation ID.

    If the client already supplied an ID,
    preserve it.

    Otherwise create a new conversation.
    """

    if conversation_id:

        conversation_id = str(
            conversation_id
        ).strip()

        if conversation_id:

            return conversation_id


    # --------------------------------------------------------
    # Create new conversation
    # --------------------------------------------------------

    try:

        conversation = create_conversation(
            "محادثة جديدة"
        )

        if isinstance(
            conversation,
            dict
        ):

            conversation_id = (
                conversation.get(
                    "id"
                )
            )

            if conversation_id:

                return str(
                    conversation_id
                )


        if conversation:

            return str(
                conversation
            )


    except Exception as e:

        print(
            "CONVERSATION CREATE ERROR:",
            repr(e)
        )


    return None


# ============================================================
# NORMALIZE BRAIN RESULT
# ============================================================

def normalize_brain_result(
    result,
    default_provider=None
):
    """
    Convert Brain's result into a predictable structure.

    Supported results:

        {
            "answer": "...",
            "imageUrl": "...",
            "provider": "..."
        }

    or:

        "IMAGE_URL:https://..."

    or:

        "normal text"
    """

    # --------------------------------------------------------
    # Dictionary result
    # --------------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        answer = result.get(
            "answer",
            ""
        )

        image_url = result.get(
            "imageUrl",
            ""
        )

        provider = result.get(
            "provider",
            default_provider
        )

        conversation_id = result.get(
            "conversation_id"
        )

        return {

            "answer":
                str(
                    answer or ""
                ),

            "imageUrl":
                str(
                    image_url or ""
                ),

            "provider":
                provider,

            "conversation_id":
                conversation_id,
        }


    # --------------------------------------------------------
    # String result
    # --------------------------------------------------------

    if isinstance(
        result,
        str
    ):

        result = result.strip()

        # ----------------------------------------------------
        # IMAGE_URL format
        # ----------------------------------------------------

        if result.startswith(
            "IMAGE_URL:"
        ):

            image_url = result[
                len("IMAGE_URL:")
            ].strip()

            return {

                "answer":
                    "تم إنشاء أو تعديل الصورة بنجاح.",

                "imageUrl":
                    image_url,

                "provider":
                    default_provider,

                "conversation_id":
                    None,
            }


        # ----------------------------------------------------
        # Normal text
        # ----------------------------------------------------

        return {

            "answer":
                result,

            "imageUrl":
                "",

            "provider":
                default_provider,

            "conversation_id":
                None,
        }


    # --------------------------------------------------------
    # Unknown result
    # --------------------------------------------------------

    return {

        "answer":
            "تعذر معالجة الطلب حاليًا.",

        "imageUrl":
            "",

        "provider":
            default_provider,

        "conversation_id":
            None,
    }


# ============================================================
# AI RESPONSE
# ============================================================

def ai_response(
    question,
    conversation_id=None
):
    """
    Handles normal TEXT requests.

    Provider routing is done inside brain.py:

        Groq
          ↓
        OpenRouter
          ↓
        Gemini

    Images are NOT processed here.
    """

    try:

        question = str(
            question or ""
        ).strip()

        if not question:

            return (
                "اكتب سؤالًا أولًا."
            )


        # ====================================================
        # CALCULATOR
        # ====================================================

        try:

            result = calculate(
                question
            )

            if result is not None:

                return (
                    f"النتيجة: {result}"
                )

        except Exception as e:

            print(
                "CALCULATOR ERROR:",
                repr(e)
            )


        # ====================================================
        # TRANSLATOR
        # ====================================================

        try:

            translated = translate(
                question
            )

            if (
                translated
                and
                str(
                    translated
                ).strip().lower()
                !=
                question.lower()
            ):

                return str(
                    translated
                )

        except Exception as e:

            print(
                "TRANSLATOR ERROR:",
                repr(e)
            )


        # ====================================================
        # MEMORY
        # ====================================================

        try:

            memory_answer = get_answer(
                question
            )

            if memory_answer:

                return memory_answer

        except Exception as e:

            print(
                "MEMORY ERROR:",
                repr(e)
            )


        # ====================================================
        # BRAIN
        # ====================================================

        try:

            result = get_response(

                question,

                conversation_id=
                    conversation_id
            )

        except TypeError as e:

            print(
                "GET_RESPONSE "
                "COMPATIBILITY ERROR:",
                repr(e)
            )

            # ------------------------------------------------
            # Compatibility with older brain.py
            # ------------------------------------------------

            result = get_response(
                question
            )


        # ====================================================
        # NORMALIZE
        # ====================================================

        normalized = normalize_brain_result(
            result
        )

        answer = normalized.get(
            "answer"
        )

        return (
            answer
            or
            "لم أجد إجابة حاليًا."
        )


    except Exception as e:

        print(
            "AI RESPONSE ERROR:",
            repr(e)
        )

        return (
            "حدث خطأ أثناء معالجة طلبك: "
            f"{e}"
        )


# ============================================================
# IMAGE REQUEST HANDLER
# ============================================================

def handle_image_request(
    image,
    question,
    conversation_id=None
):
    """
    Handles uploaded images.

    IMPORTANT:

    This function DOES NOT call Groq Vision,
    OpenRouter Vision or Gemini Vision.

    It sends the image to:

        brain.get_image_response()

    and Brain routes it to:

        MISTRAL ONLY
    """

    if image is None:

        return {

            "answer":
                "لم يتم إرسال صورة.",

            "imageUrl":
                "",

            "provider":
                None,
        }


    if not image.filename:

        return {

            "answer":
                "لم يتم اختيار صورة.",

            "imageUrl":
                "",

            "provider":
                None,
        }


    try:

        print("=" * 70)

        print(
            "IMAGE REQUEST RECEIVED"
        )

        print(
            "FILENAME:",
            image.filename
        )


        # ====================================================
        # READ IMAGE
        # ====================================================

        image_bytes = image.read()


        # ====================================================
        # MIME
        # ====================================================

        mime_type = (
            image.mimetype
            or "image/jpeg"
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


        # ====================================================
        # VALIDATION
        # ====================================================

        if not image_bytes:

            return {

                "answer":
                    "لم يتم إرسال بيانات صورة صالحة.",

                "imageUrl":
                    "",

                "provider":
                    None,
            }


        if not mime_type.startswith(
            "image/"
        ):

            return {

                "answer":
                    "الملف المرسل ليس صورة صالحة.",

                "imageUrl":
                    "",

                "provider":
                    None,
            }


        # ====================================================
        # IMAGE QUESTION
        # ====================================================

        image_question = str(
            question or ""
        ).strip()


        if not image_question:

            image_question = (
                "حلل هذه الصورة واشرح لي "
                "بالتفصيل ما الذي يظهر فيها."
            )


        print(
            "IMAGE QUESTION:",
            image_question
        )

        print(
            "CONVERSATION ID:",
            conversation_id
        )

        print(
            "IMAGE PROVIDER: MISTRAL ONLY"
        )

        print("=" * 70)


        # ====================================================
        # SEND TO BRAIN
        # ====================================================

        try:

            result = get_image_response(

                image_question,

                image_bytes,

                mime_type,

                conversation_id=
                    conversation_id
            )

        except TypeError as e:

            print(
                "GET_IMAGE_RESPONSE "
                "COMPATIBILITY ERROR:",
                repr(e)
            )

            # ------------------------------------------------
            # Compatibility with an older brain.py
            # ------------------------------------------------

            result = get_image_response(

                image_question,

                image_bytes,

                mime_type
            )


        # ====================================================
        # NORMALIZE IMAGE RESULT
        # ====================================================

        normalized = normalize_brain_result(

            result,

            default_provider="Mistral"
        )


        answer = normalized.get(
            "answer"
        )

        image_url = normalized.get(
            "imageUrl"
        )

        provider = normalized.get(
            "provider"
        )


        # ====================================================
        # LOG
        # ====================================================

        print("=" * 70)

        print(
            "IMAGE PROCESSING COMPLETE"
        )

        print(
            "PROVIDER:",
            provider
        )

        print(
            "HAS GENERATED IMAGE:",
            bool(image_url)
        )

        print(
            "ANSWER:",
            answer
        )

        print("=" * 70)


        return {

            "answer":
                answer
                or
                "تمت معالجة الصورة.",

            "imageUrl":
                image_url
                or
                "",

            "provider":
                provider
                or
                "Mistral",
        }


    except Exception as e:

        print("=" * 70)

        print(
            "IMAGE ERROR:",
            repr(e)
        )

        print("=" * 70)

        return {

            "answer":
                (
                    "حدث خطأ أثناء معالجة "
                    "الصورة عبر Mistral: "
                    f"{e}"
                ),

            "imageUrl":
                "",

            "provider":
                "Mistral",
        }


# ============================================================
# HOME
# ============================================================

@app.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
def home():

    answer = ""

    generated_image = None

    provider = None


    # ========================================================
    # CURRENT TIME
    # ========================================================

    current_time = (
        datetime.now()
        .strftime(
            "%H:%M:%S"
        )
    )


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        # ====================================================
        # QUESTION
        # ====================================================

        question = request.form.get(

            "question",

            ""
        ).strip()


        # ====================================================
        # CONVERSATION ID
        # ====================================================

        conversation_id = request.form.get(

            "conversation_id",

            ""
        ).strip()


        conversation_id = (
            resolve_conversation_id(
                conversation_id
            )
        )


        # ====================================================
        # IMAGE FILE
        # ====================================================

        image = request.files.get(
            "image"
        )


        # ====================================================
        # IMAGE REQUEST
        # ====================================================

        if (
            image
            and
            image.filename
        ):

            image_result = handle_image_request(

                image,

                question,

                conversation_id
            )


            # ------------------------------------------------
            # Put result into page variables
            # ------------------------------------------------

            answer = image_result.get(
                "answer",
                ""
            )

            generated_image = (
                image_result.get(
                    "imageUrl",
                    ""
                )
                or
                None
            )

            provider = (
                image_result.get(
                    "provider"
                )
                or
                "Mistral"
            )


        # ====================================================
        # NORMAL TEXT REQUEST
        # ====================================================

        elif question:

            answer = ai_response(

                question,

                conversation_id=
                    conversation_id
            )

            provider = None


    # ========================================================
    # RENDER
    # ========================================================

    return render_template(

        "page.html",

        answer=answer,

        generated_image=
            generated_image,

        provider=
            provider,

        time=
            current_time
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return {

        "status":
            "ok",

        "app":
            "IDO AI",

        "text":
            [
                "Groq",
                "OpenRouter",
                "Gemini"
            ],

        "images":
            [
                "Mistral"
            ]
    }


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return {

        "error":
            "Not Found",

        "message":
            "المسار المطلوب غير موجود."
    }, 404


@app.errorhandler(500)
def internal_error(error):

    print(
        "FLASK 500 ERROR:",
        repr(error)
    )

    return {

        "error":
            "Internal Server Error",

        "message":
            "حدث خطأ داخلي في الخادم."
    }, 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    port = int(

        os.environ.get(

            "PORT",

            5000
        )
    )


    print("=" * 70)

    print(
        "IDO AI STARTING"
    )

    print(
        "PORT:",
        port
    )

    print(
        "TEXT PROVIDERS:"
    )

    print(
        "    GROQ"
    )

    print(
        "    OPENROUTER"
    )

    print(
        "    GEMINI"
    )

    print(
        "IMAGE PROVIDER:"
    )

    print(
        "    MISTRAL ONLY"
    )

    print("=" * 70)


    app.run(

        host="0.0.0.0",

        port=port,

        debug=True
    )