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


    message = data.get("message", "")


    if not message:
        return jsonify({
            "answer": "اكتب رسالة"
        })


    # إرسال الرسالة إلى عقل Ido AI
    answer = get_response(message)


    return jsonify({
        "answer": answer
    })