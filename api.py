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
# إنشاء / استرجاع Conversation ID
# =========================================================

def resolve_conversation_id(
    conversation_id=None
):

    # -----------------------------------------------------
    # إذا كان المعرف موجودًا بالفعل
    # -----------------------------------------------------

    if conversation_id:

        conversation_id = str(
            conversation_id
        ).strip()

        if conversation_id:

            return conversation_id


    # -----------------------------------------------------
    # إنشاء محادثة جديدة
    # -----------------------------------------------------

    try:

        conversation = create_conversation(
            "محادثة جديدة"
        )


        if isinstance(
            conversation,
            dict
        ):

            return conversation.get(
                "id"
            )


        if conversation:

            return str(
                conversation
            )


    except Exception as e:

        print(
            "CONVERSATION CREATE ERROR:",
            repr(e)
        )


    return None


# =========================================================
# Chat API
# =========================================================

@api.route(
    "/api/chat",
    methods=["POST"]
)
def chat_api():

    # =====================================================
    # قراءة JSON
    # =====================================================

    try:

        data = request.get_json(
            silent=True
        )

    except Exception as e:

        print(
            "JSON READ ERROR:",
            repr(e)
        )

        return jsonify({

            "answer":
                "تعذر قراءة الطلب.",

            "error":
                str(e)

        }), 400


    # =====================================================
    # التحقق من البيانات
    # =====================================================

    if not data:

        return jsonify({

            "answer":
                "لم يتم إرسال بيانات.",

            "error":
                "No data received"

        }), 400


    # =====================================================
    # قراءة الرسالة
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

            "answer":
                "اكتب رسالة أولًا."

        })


    # =====================================================
    # Conversation ID
    # =====================================================

    conversation_id = (
        data.get(
            "conversation_id"
        )
    )


    conversation_id = (
        resolve_conversation_id(
            conversation_id
        )
    )


    # =====================================================
    # تسجيل الطلب
    # =====================================================

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


    # =====================================================
    # إرسال الرسالة إلى Brain
    # =====================================================

    try:

        # -------------------------------------------------
        # نحاول أولًا النسخة الجديدة التي تدعم
        # conversation_id
        # -------------------------------------------------

        try:

            answer = get_response(
                message,
                conversation_id=conversation_id
            )


        except TypeError as e:

            print(
                "GET_RESPONSE COMPATIBILITY:",
                repr(e)
            )

            # -------------------------------------------------
            # توافق مع brain.py قديم
            # -------------------------------------------------

            answer = get_response(
                message
            )


        # =================================================
        # معالجة نتيجة Brain
        # =================================================

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
        # تسجيل النجاح
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


        print("=" * 60)


        # =================================================
        # إرسال JSON
        # =================================================

        return jsonify(
            response_data
        )


    # =====================================================
    # خطأ Brain
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