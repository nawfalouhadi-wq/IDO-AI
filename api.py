from flask import Blueprint, request, jsonify

from brain import get_response
from memory import create_conversation


# =========================================================
# API BLUEPRINT
# =========================================================

api = Blueprint(
    "api",
    __name__
)


# =========================================================
# CONVERSATION ID
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

            conversation_id = (
                conversation.get("id")
            )

            if conversation_id:
                return str(
                    conversation_id
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
# CHAT API
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
                str(e),

            "imageUrl":
                "",

            "provider":
                None

        }), 400


    # =====================================================
    # التحقق من البيانات
    # =====================================================

    if not isinstance(
        data,
        dict
    ):

        return jsonify({

            "answer":
                "لم يتم إرسال بيانات صحيحة.",

            "error":
                "Invalid JSON data",

            "imageUrl":
                "",

            "provider":
                None

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
                "اكتب رسالة أولًا.",

            "imageUrl":
                "",

            "provider":
                None

        }), 400


    # =====================================================
    # Conversation ID
    # =====================================================

    conversation_id = data.get(
        "conversation_id"
    )


    conversation_id = (
        resolve_conversation_id(
            conversation_id
        )
    )


    # =====================================================
    # LOG
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
    # إرسال الطلب إلى Brain
    # =====================================================

    try:

        try:

            answer = get_response(
                message,
                conversation_id=conversation_id
            )

        except TypeError:

            print(
                "GET_RESPONSE COMPATIBILITY:"
                " conversation_id unsupported"
            )

            answer = get_response(
                message
            )


        # =================================================
        # Brain أعاد Dictionary
        #
        # مثال:
        #
        # {
        #     "answer": "...",
        #     "imageUrl": "...",
        #     "provider": "Gemini"
        # }
        # =================================================

        if isinstance(
            answer,
            dict
        ):

            response_data = {

                "answer":
                    str(
                        answer.get(
                            "answer",
                            "تم تنفيذ الطلب."
                        )
                        or
                        "تم تنفيذ الطلب."
                    ),

                "conversation_id":
                    conversation_id,

                "imageUrl":
                    str(
                        answer.get(
                            "imageUrl",
                            ""
                        )
                        or
                        ""
                    ),

                "provider":
                    answer.get(
                        "provider"
                    )

            }


        # =================================================
        # Brain أعاد نصًا عاديًا
        # =================================================

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
                    "Groq"

            }


        # =================================================
        # LOG SUCCESS
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
            (
                "YES"
                if response_data.get(
                    "imageUrl"
                )
                else "NO"
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
        # JSON RESPONSE
        # =================================================

        return jsonify(
            response_data
        )


    # =====================================================
    # BRAIN ERROR
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
                "الرسالة في Ido AI.",

            "error":
                str(e),

            "conversation_id":
                conversation_id,

            "imageUrl":
                "",

            "provider":
                None

        }), 500