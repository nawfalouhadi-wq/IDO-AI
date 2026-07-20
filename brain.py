def get_response(message):
    message = message.lower().strip()

    if "hello" in message or "hi" in message:
        return "Hello! أنا Ido AI 🤖"

    if "مرحبا" in message or "سلام" in message:
        return "مرحبًا بك! كيف يمكنني مساعدتك؟ 😊"

    if "اسمك" in message:
        return "أنا Ido AI"

    return "لم أفهم سؤالك بعد، لكنني أتعلم يومًا بعد يوم 🤖"