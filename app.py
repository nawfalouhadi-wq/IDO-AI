from flask import Flask, render_template, request
from datetime import datetime

from brain import get_response
from calculator import calculate
from translator import translate
from memory import get_answer
from ollama_ai import ask_ollama


app = Flask(__name__, template_folder=".")



def ai_response(question):

    try:

        question = question.strip()


        # 1 - الحاسبة
        calc = calculate(question)

        if calc is not None:
            return f"🧮 النتيجة: {calc}"



        # 2 - الترجمة
        translated = translate(question)

        if translated.lower() != question.lower():
            return f"🌍 {translated}"



        # 3 - الذاكرة
        saved = get_answer(question)

        if saved:
            return saved



        # 4 - عقل Ido AI
        answer = get_response(question)



        # 5 - إذا احتاج نموذج Ollama
        if (
            "لم أفهم" in answer
            or "لا أعرف" in answer
            or answer.strip() == ""
        ):

            return ask_ollama(question)



        return answer



    except Exception as e:

        return f"حدث خطأ: {e}"





@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""

    time = datetime.now().strftime("%H:%M:%S")



    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        )


        if question.strip():

            answer = ai_response(question)



    return render_template(
        "page.html",
        answer=answer,
        time=time
    )





if __name__ == "__main__":

    app.run(debug=True)
