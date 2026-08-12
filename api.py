# ============================================================
# OVERRIDE get_response
# ============================================================
#
# هذا التعريف يحل مشكلة:
#
# NameError:
# name 'quick_response' is not defined
#
# ويجعل get_response يعمل حتى إذا لم تكن
# quick_response موجودة في brain.py الأصلي.
#
# ============================================================

def get_response(
    message,
    conversation_id=None
):

    # ========================================================
    # التحقق من الرسالة
    # ========================================================

    if not message:

        return (
            "اكتب رسالة أولًا."
        )

    original_message = str(
        message
    ).strip()

    if not original_message:

        return (
            "اكتب رسالة أولًا."
        )


    # ========================================================
    # IMAGE GENERATION
    # ========================================================
    #
    # يجب فحص طلب إنشاء الصورة أولًا.
    #
    # حتى لا يتم إرساله إلى مزود النص بالخطأ.
    #
    # ========================================================

    try:

        if _smart_is_generation_request(
            original_message
        ):

            prompt = _advanced_image_prompt(
                original_message
            )

            if prompt:

                print("=" * 60)

                print(
                    "ADVANCED TEXT -> IMAGE REQUEST"
                )

                print(
                    "IMAGE PROMPT:",
                    prompt
                )

                print("=" * 60)

                result = _advanced_generate_image_chain(
                    prompt
                )

                return result

    except Exception as exc:

        print(
            "IMAGE GENERATION ROUTER ERROR:",
            exc
        )


    # ========================================================
    # QUICK RESPONSE
    # ========================================================
    #
    # quick_response قد تكون موجودة في بعض نسخ brain.py
    # وغير موجودة في نسخ أخرى.
    #
    # لذلك نتحقق منها بطريقة آمنة.
    #
    # ========================================================

    try:

        quick_function = globals().get(
            "quick_response"
        )

        if callable(
            quick_function
        ):

            quick = quick_function(
                original_message
            )

            if quick:

                return quick

    except Exception as exc:

        print(
            "QUICK RESPONSE ERROR:",
            exc
        )


    # ========================================================
    # TEXT FAILOVER
    # ========================================================

    routes = [

        (
            "GROQ",
            ask_groq
        ),

        (
            "MISTRAL",
            ask_mistral
        ),

        (
            "OPENROUTER",
            ask_openrouter
        ),

        (
            "GEMINI",
            ask_gemini
        ),

        (
            "XAI",
            ask_xai
        ),

        (
            "POLLINATIONS",
            ask_pollinations
        )
    ]


    attempts = 0


    # ========================================================
    # تجربة مزودي الذكاء الاصطناعي
    # ========================================================

    for name, function in routes:

        if attempts >= (
            ADVANCED_MAX_PROVIDER_ATTEMPTS
        ):

            print(
                "Maximum provider attempts reached."
            )

            break


        attempts += 1


        # ----------------------------------------------------
        # التحقق من توفر المزود
        # ----------------------------------------------------

        try:

            if not provider_available(
                name
            ):

                print(
                    f"{name}: SKIPPED "
                    "(cooldown)"
                )

                continue

        except Exception as exc:

            print(
                f"{name} AVAILABILITY ERROR:",
                exc
            )

            continue


        print("=" * 40)

        print(
            "ADVANCED TEXT TRY:",
            name
        )

        print("=" * 40)


        # ----------------------------------------------------
        # إرسال الرسالة
        # ----------------------------------------------------

        try:

            answer = function(
                original_message
            )

        except Exception as exc:

            _provider_stat(
                name,
                failure=True
            )

            print(
                f"{name} ROUTER ERROR:",
                exc
            )

            answer = None


        # ----------------------------------------------------
        # نجاح
        # ----------------------------------------------------

        if answer:

            _provider_stat(
                name,
                success=True
            )

            print(
                "TEXT ROUTE SUCCESS:",
                name
            )

            return answer


        # ----------------------------------------------------
        # فشل وانتقال للمزود التالي
        # ----------------------------------------------------

        print(
            f"{name} failed. "
            "Trying next provider..."
        )


        if ADVANCED_RETRY_DELAY > 0:

            time.sleep(
                ADVANCED_RETRY_DELAY
            )


    # ========================================================
    # فشل جميع المزودين
    # ========================================================

    return (
        "أنا Ido AI، لكن جميع مزودي "
        "الذكاء الاصطناعي المتاحين "
        "فشلوا حاليًا. "
        "تحقق من المفاتيح والرصيد "
        "وحالة مزودي الخدمة."
    )