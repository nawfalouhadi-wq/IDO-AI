# ============================================================
# SAFE QUICK RESPONSE
# ============================================================
#
# بعض نسخ brain.py تستدعي:
#
#     quick_response(message)
#
# لكن الدالة قد لا تكون موجودة في النسخة الحالية.
#
# لذلك نضيف نسخة آمنة.
#
# إذا كانت quick_response الأصلية موجودة، فلا نحتاج إلى
# استخدامها هنا في الحالات العادية.
#
# إذا لم تكن موجودة، هذه الدالة ترجع None فقط،
# وبالتالي يكمل النظام إلى مزودي الذكاء الاصطناعي.
#
# ============================================================

def quick_response(message):

    # --------------------------------------------------------
    # التحقق من الرسالة
    # --------------------------------------------------------

    if not message:

        return None


    message = str(
        message
    ).strip()


    if not message:

        return None


    # --------------------------------------------------------
    # ردود سريعة بسيطة
    # --------------------------------------------------------

    normalized = message.lower()


    # العربية
    if normalized in (
        "مرحبا",
        "مرحباً",
        "اهلا",
        "أهلا",
        "اهلاً",
        "السلام عليكم"
    ):

        return (
            "مرحبًا! أنا Ido AI 🤖 "
            "كيف يمكنني مساعدتك؟"
        )


    # English
    if normalized in (
        "hello",
        "hi",
        "hey"
    ):

        return (
            "Hello! I'm Ido AI 🤖 "
            "How can I help you?"
        )


    # --------------------------------------------------------
    # لا يوجد رد سريع
    #
    # دع الرسالة تمر إلى مزودي الذكاء الاصطناعي.
    # --------------------------------------------------------

    return None


# ============================================================
# OVERRIDE get_response
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


                result = (
                    _advanced_generate_image_chain(
                        prompt
                    )
                )


                return result


    except Exception as exc:

        print(
            "IMAGE GENERATION ROUTER ERROR:",
            repr(exc)
        )


    # ========================================================
    # QUICK RESPONSE
    # ========================================================

    try:

        quick = quick_response(
            original_message
        )


        if quick:

            return quick


    except Exception as exc:

        print(
            "QUICK RESPONSE ERROR:",
            repr(exc)
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
                repr(exc)
            )

            continue


        print("=" * 40)

        print(
            "ADVANCED TEXT TRY:",
            name
        )

        print("=" * 40)


        # ----------------------------------------------------
        # استدعاء المزود
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
                repr(exc)
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
        # الانتقال إلى المزود التالي
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