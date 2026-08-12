from flask import Flask, render_template, request
from datetime import datetime
import os

from brain import (
    get_response,
    get_image_response
)

from calculator import calculate
from translator import translate
from memory import (
    get_answer,
    create_conversation
)


# =========================================================
# API
# =========================================================

try:

    from api import api

    api_available = True

except Exception as e:

    print(
        "API error:",
        e
    )

    api_available = False


# =========================================================
# إنشاء تطبيق Flask
# =========================================================

app = Flask(
    __name__,
    template_folder="templates"
)


# =========================================================
# تسجيل API
# =========================================================

if api_available:

    app.register_blueprint(
        api
    )


# =========================================================
# إنشاء / استرجاع معرف المحادثة
# =========================================================

def resolve_conversation_id(
    conversation_id=None
):

    if conversation_id:

        return str(
            conversation_id
        ).strip()

    try:

        conversation = (
            create_conversation(
                "محادثة جديدة"
            )
        )

        if isinstance(
            conversation,
            dict
        ):

            return conversation.get(
                "id"
            )

        return str(
            conversation
        )

    except Exception as e:

        print(
            "CONVERSATION CREATE ERROR:",
            e
        )

        return None


# =========================================================
# Ido AI Response
# =========================================================

def ai_response(
    question,
    conversation_id=None
):

    try:

        question = (
            str(question)
            .strip()
        )

        if not question:

            return (
                "اكتب سؤالاً أولاً"
            )

        # =====================================================
        # الحاسبة
        # =====================================================

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
                e
            )

        # =====================================================
        # الترجمة
        # =====================================================

        try:

            translated = translate(
                question
            )

            if (
                translated
                and translated.lower()
                != question.lower()
            ):

                return translated

        except Exception as e:

            print(
                "TRANSLATOR ERROR:",
                e
            )

        # =====================================================
        # الذاكرة
        # =====================================================

        try:

            memory_answer = get_answer(
                question
            )

            if memory_answer:

                return memory_answer

        except Exception as e:

            print(
                "MEMORY ERROR:",
                e
            )

        # =====================================================
        # Gemini / OpenRouter / Groq / Mistral
        # =====================================================

        answer = get_response(
            question,
            conversation_id=conversation_id
        )

        return (
            answer
            or "لم أجد إجابة حاليًا."
        )

    except Exception as e:

        print(
            "AI RESPONSE ERROR:",
            e
        )

        return f"خطأ: {e}"


# =========================================================
# الصفحة الرئيسية
# =========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    answer = ""

    generated_image = None

    current_time = (
        datetime.now()
        .strftime("%H:%M:%S")
    )

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        # =====================================================
        # معرف المحادثة
        # =====================================================

        conversation_id = request.form.get(
            "conversation_id",
            ""
        ).strip()

        conversation_id = (
            resolve_conversation_id(
                conversation_id
            )
        )

        # =====================================================
        # رفع صورة
        # =====================================================

        image = request.files.get(
            "image"
        )

        if image and image.filename:

            try:

                print(
                    "IMAGE REQUEST RECEIVED"
                )

                image_bytes = image.read()

                mime_type = (
                    image.mimetype
                    or "image/jpeg"
                )

                if not image_bytes:

                    answer = (
                        "لم يتم اختيار "
                        "صورة صالحة."
                    )

                elif not mime_type.startswith(
                    "image/"
                ):

                    answer = (
                        "الملف المرسل ليس "
                        "صورة صالحة."
                    )

                else:

                    # =========================================
                    # سؤال الصورة
                    # =========================================

                    if question:

                        image_question = (
                            question
                        )

                    else:

                        image_question = (
                            "حلل هذه الصورة "
                            "واشرح لي بالتفصيل "
                            "ما الذي يظهر فيها."
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
                        image_question
                    )

                    print(
                        "CONVERSATION ID:",
                        conversation_id
                    )

                    # =========================================
                    # تحليل / تعديل الصورة
                    # =========================================

                    result = get_image_response(
                        image_question,
                        image_bytes,
                        mime_type,
                        conversation_id=conversation_id
                    )

                    # =========================================
                    # هل النتيجة صورة مولدة؟
                    # =========================================

                    if (
                        isinstance(
                            result,
                            str
                        )
                        and result.startswith(
                            "IMAGE_URL:"
                        )
                    ):

                        generated_image = (
                            result[
                                len("IMAGE_URL:"):
                            ].strip()
                        )

                        answer = (
                            "تم تعديل الصورة "
                            "بناءً على طلبك."
                        )

                        print(
                            "GENERATED IMAGE:",
                            generated_image
                        )

                    else:

                        answer = (
                            result
                            or
                            "تعذر معالجة "
                            "الصورة حاليًا."
                        )

            except Exception as e:

                print(
                    "IMAGE ERROR:",
                    e
                )

                answer = (
                    "حدث خطأ أثناء "
                    "معالجة الصورة: "
                    f"{e}"
                )

        # =====================================================
        # سؤال نصي عادي
        # =====================================================

        elif question:

            answer = ai_response(
                question,
                conversation_id=conversation_id
            )

    return render_template(
        "page.html",
        answer=answer,
        generated_image=generated_image,
        time=current_time
    )


# =========================================================
# تشغيل التطبيق
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )