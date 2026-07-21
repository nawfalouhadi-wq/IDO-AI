from flask import Flask, render_template, request
from datetime import datetime
import os

from brain import get_response
from calculator import calculate
from translator import translate
from memory import get_answer


# استيراد API
try:
    from api import api
    api_available = True
except Exception as e:
    print("API error:", e)
    api_available = False


# إنشاء تطبيق Flask
app = Flask(
    __name__,
    template_folder="templates"
)


# تسجيل API
if api_available:
    app.register_blueprint(api)


def ai_response(question):

    try:
        question = question.strip()

        if not question:
            return "اكتب سؤالاً أولاً"


        # الحاسبة
        try:
            result = calculate(question)

            if result is not None:
                return f"🧮 النتيجة: {result}"

        except Exception:
            pass


        # الترجمة
        try:
            translated = translate(question)

            if translated and translated.lower() != question.lower():
                return f"🌍 {translated}"

        except Exception:
            pass


        # الذاكرة
        try:
            memory_answer = get_answer(question)

            if memory_answer:
                return memory_answer

        except Exception:
            pass


        # عقل Ido AI
        answer = get_response(question)


        if not answer:
            answer = "لم أفهم السؤال"


        return answer


    except Exception as e:
        return f"⚠️ خطأ: {e}"



@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    current_time = datetime.now().strftime("%H:%M:%S")


    if request.method == "POST":

        question = request.form.get("question", "")

        if question.strip():
            answer = ai_response(question)


    return render_template(
        "page.html",
        answer=answer,
        time=current_time
    )



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )