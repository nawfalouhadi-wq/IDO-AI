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

    try:

        data = request.get_json(
            silent=True
        )

    except Exception as e:

        print(
            "JSON READ ERROR:",
            e
        )

        return jsonify({
            "answer": "تعذر قراءة الطلب.",
            "error": str(e)
        }), 400


    if not data:

        return jsonify({
            "answer": "لم يتم إرسال بيانات.",
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
            "answer": "اكتب رسالة أولًا."
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

        print("=" * 60)

        print(
            "API CHAT REQUEST"
        )

        print(
            "MESSAGE:",
            message
        )

        print(
            "CONVERSATION ID:",
            conversation_id
        )

        print("=" * 60)


        # -------------------------------------------------
        # brain.py الحالي
        # -------------------------------------------------

        answer = get_response(
            message,
            conversation_id=conversation_id
        )


        # =================================================
        # معالجة نتيجة Brain
        # =================================================

        # -------------------------------------------------
        # الحالة 1:
        # Brain رجع Dictionary
        #
        # مثال إنشاء صورة:
        #
        # {
        #     "answer": "...",
        #     "imageUrl": "...",
        #     "provider": "xAI"
        # }
        # -------------------------------------------------

        if isinstance(
            answer,
            dict
        ):

            response_data = {

                "answer":
                    answer.get(
                        "answer",
                        "تم تنفيذ الطلب."
                    ),

                "conversation_id":
                    conversation_id,

                "imageUrl":
                    answer.get(
                        "imageUrl",
                        ""
                    ),

                "provider":
                    answer.get(
                        "provider"
                    )
            }


        # -------------------------------------------------
        # الحالة 2:
        # Brain رجع نصًا
        # -------------------------------------------------

        else:

            response_data = {

                "answer":
                    str(
                        answer
                        or
                        "لم أجد إجابة حاليًا."
                    ),

                "conversation_id":
                    conversation_id,

                "imageUrl":
                    "",

                "provider":
                    None
            }


        # =================================================
        # إرسال النتيجة
        # =================================================

        print(
            "API CHAT SUCCESS"
        )

        print(
            "ANSWER:",
            response_data.get(
                "answer"
            )
        )

        print(
            "IMAGE URL:",
            response_data.get(
                "imageUrl"
            )
        )

        print(
            "PROVIDER:",
            response_data.get(
                "provider"
            )
        )


        return jsonify(
            response_data
        )


    # =====================================================
    # خطأ أثناء تشغيل Brain
    # =====================================================

    except Exception as e:

        print("=" * 60)

        print(
            "API CHAT ERROR:"
        )

        print(
            repr(e)
        )

        print("=" * 60)


        return jsonify({

            "answer":
                "حدث خطأ أثناء معالجة "
                "الرسالة في Aido AI.",

            "error":
                str(e),

            "conversation_id":
                conversation_id,

            "imageUrl":
                "",

            "provider":
                None

        }), 500