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


# Flask يبحث الآن داخل مجلد templates
app = Flask(__name__)


def ai_response(question):

    try:
        question = question.strip()

        if not question:
            return "اكتب سؤالاً أولاً"


        # 1 - الحاسبة
        try:
            calc = calculate(question)

            if calc is not None:
                return f"🧮 النتيجة: {calc}"

        except Exception:
            pass



        # 2 - الترجمة
        try:
            translated = translate(question)

            if translated and translated.lower() != question.lower():
                return f"🌍 {translated}"

        except Exception:
            pass



        # 3 - الذاكرة
        try:
            saved = get_answer(question)

            if saved:
                return saved

        except Exception:
            pass



        # 4 - عقل Ido AI
        answer = get_response(question)


        if not answer:
            answer = "لم أفهم السؤال"



        # 5 - Ollama إذا لم يجد جواباً
        if (
            "لم أفهم" in answer
            or "لا أعرف" in answer
            or answer.strip() == ""
        ):

            if ollama_available:
                return ask_ollama(question)



        return answer



    except Exception as e:

        return f"⚠️ حدث خطأ: {str(e)}"



@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    current_time = datetime.now().strftime("%H:%M:%S")


    if request.method == "POST":

        question = request.form.get("question", "")

        answer = ai_response(question)



    return render_template(
        "page.html",
        answer=answer,
        time=current_time
    )



# تشغيل التطبيق
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )