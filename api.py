from flask import Blueprint, request, jsonify

from brain import get_response

from memory import create_conversation


# =========================================================
# إنشاء API Blueprint
# =========================================================

api = Blueprint(
    "api",
    __name__
)


# =========================================================
# Chat API
# =========================================================

@api.route(
    "/api/chat",
    methods=["POST"]
)
def chat_api():

    data = request.get_json(
        silent=True
    )

    # =====================================================
    # التحقق من البيانات
    # =====================================================

    if not data:

        return jsonify({
            "error":
                "No data received"
        }), 400

    message = data.get(
        "message",
        ""
    )

    if message is None:
        message = ""

    message = str(
        message
    ).strip()

    if not message:

        return jsonify({
            "answer":
                "اكتب رسالة"
        })

    # =====================================================
    # الحصول على معرف المحادثة
    # =====================================================

    conversation_id = data.get(
        "conversation_id"
    )

    if conversation_id:

        conversation_id = str(
            conversation_id
        ).strip()

    # =====================================================
    # إنشاء محادثة جديدة إذا لم يوجد معرف
    # =====================================================

    if not conversation_id:

        try:

            conversation = (
                create_conversation(
                    "محادثة جديدة"
                )
            )

            conversation_id = (
                conversation.get(
                    "id"
                )
                if isinstance(
                    conversation,
                    dict
                )
                else conversation
            )

        except Exception as e:

            print(
                "CONVERSATION CREATE ERROR:",
                e
            )

            conversation_id = None

    # =====================================================
    # إرسال الرسالة إلى عقل Ido AI
    # =====================================================

    try:

        answer = get_response(
            message,
            conversation_id=conversation_id
        )

        return jsonify({

            "answer":
                answer
                or "لم أجد إجابة حاليًا.",

            "conversation_id":
                conversation_id

        })

    except Exception as e:

        print(
            "API CHAT ERROR:",
            e
        )

        return jsonify({

            "answer":
                f"حدث خطأ: {e}",

            "conversation_id":
                conversation_id

        }), 500