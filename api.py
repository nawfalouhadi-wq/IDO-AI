from flask import Blueprint, request, jsonify
from brain import get_response

api = Blueprint("api", __name__)


@api.route("/api/chat", methods=["POST"])
def chat_api():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "answer": "اكتب رسالة"
        })

    # =========================
    # إرسال الرسالة إلى عقل Aido AI
    # =========================

    try:

        answer = get_response(message)

        return jsonify({
            "answer": answer or "لم أجد إجابة حاليًا."
        })

    except Exception as e:

        print("API CHAT ERROR:", e)

        return jsonify({
            "answer": f"حدث خطأ: {e}"
        }), 500