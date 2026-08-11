from flask import Flask, render_template, request
from datetime import datetime
import os

from brain import get_response, get_image_response
from calculator import calculate
from translator import translate
from memory import get_answer

# =========================
# API
# =========================

try:
    from api import api
    api_available = True
except Exception as e:
    print("API error:", e)
    api_available = False

# =========================
# إنشاء تطبيق Flask
# =========================

app = Flask(
    __name__,
    template_folder="templates"
)

# =========================
# تسجيل API
# =========================

if api_available:
    app.register_blueprint(api)

# =========================
# Ido AI Response
# =========================

def ai_response(question):

    try:
        question = question.strip()

        if not question:
            return "اكتب سؤالاً أولاً"

        # =========================
        # الحاسبة
        # =========================

        try:
            result = calculate(question)

            if result is not None:
                return f"النتيجة: {result}"

        except Exception as e:
            print("CALCULATOR ERROR:", e)

        # =========================
        # الترجمة
        # =========================

        try:
            translated = translate(question)

            if translated and translated.lower() != question.lower():
                return translated

        except Exception as e:
            print("TRANSLATOR ERROR:", e)

        # =========================
        # الذاكرة
        # =========================

        try:
            memory_answer = get_answer(question)

            if memory_answer:
                return memory_answer

        except Exception as e:
            print("MEMORY ERROR:", e)

        # =========================
        # Gemini / OpenRouter / OpenAI
        # =========================

        answer = get_response(question)

        return answer or "لم أجد إجابة حاليًا."

    except Exception as e:

        print("AI RESPONSE ERROR:", e)

        return f"خطأ: {e}"


# =========================
# الصفحة الرئيسية
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    current_time = datetime.now().strftime("%H:%M:%S")

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        # =========================
        # رفع صورة
        # =========================

        image = request.files.get("image")

        if image and image.filename:

            try:

                image_bytes = image.read()

                mime_type = image.mimetype

                if not image_bytes:

                    answer = "لم يتم اختيار صورة صالحة."

                else:

                    if question:

                        image_question = question

                    else:

                        image_question = (
                            "حلل هذه الصورة واشرح لي بالتفصيل "
                            "ما الذي يظهر فيها."
                        )

                    answer = get_image_response(
                        image_question,
                        image_bytes,
                        mime_type
                    )

                    if not answer:
                        answer = "تعذر تحليل الصورة حاليًا."

            except Exception as e:

                print("IMAGE ERROR:", e)

                answer = (
                    "حدث خطأ أثناء تحليل الصورة: "
                    f"{e}"
                )

        # =========================
        # سؤال نصي عادي
        # =========================

        elif question:

            answer = ai_response(question)

    return render_template(
        "page.html",
        answer=answer,
        time=current_time
    )


# =========================
# تشغيل التطبيق
# =========================

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