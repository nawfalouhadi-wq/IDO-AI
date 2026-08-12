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

    # =====================================================
    # قراءة البيانات
    # =====================================================

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "error": "No data received"
        }), 400


    # =====================================================
    # الحصول على الرسالة
    # =====================================================

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
            "answer": "اكتب رسالة"
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

            conversation = create_conversation(
                "محادثة جديدة"
            )

            if isinstance(
                conversation,
                dict
            ):

                conversation_id = (
                    conversation.get("id")
                )

            else:

                conversation_id = str(
                    conversation
                )

        except Exception as e:

            print(
                "CONVERSATION CREATE ERROR:",
                e
            )

            conversation_id = None


    # =====================================================
    # إرسال الرسالة إلى Brain
    # =====================================================

    try:

        # -------------------------------------------------
        # مهم جدًا:
        #
        # brain.py الحالي لا يستقبل conversation_id
        # لذلك نرسل الرسالة فقط.
        # -------------------------------------------------

        answer = get_response(
            message
        )


        # =================================================
        # إرسال النتيجة
        # =================================================

        return jsonify({

            "answer": (
                answer
                or "لم أجد إجابة حاليًا."
            ),

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