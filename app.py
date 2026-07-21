from flask import Flask, render_template, request
from datetime import datetime
import os

from brain import get_response
from calculator import calculate
from translator import translate
from memory import get_answer


# استيراد Ollama بشكل آمن
try:
    from ollama_ai import ask_ollama
    ollama_available = True
except Exception:
    ollama_available = False


# Flask سيبحث تلقائياً داخل مجلد templates
app = Flask(__name__)


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


        # Ollama عند الحاجة فقط
        if (
            ("لم أفهم" in answer or "لا أعرف" in answer)
            and ollama_available
        ):
            try:
                return ask_ollama(question)
            except Exception:
                pass


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



# تشغيل محلي فقط
# Railway يستخدم gunicorn app:app
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )