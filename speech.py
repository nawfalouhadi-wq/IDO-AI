import speech_recognition as sr


def listen():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("🎤 تحدث الآن...")

            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )


        text = recognizer.recognize_google(
            audio,
            language="ar-SA"
        )


        return text



    except sr.WaitTimeoutError:

        return "لم يتم اكتشاف صوت."



    except sr.UnknownValueError:

        return "لم أفهم الصوت."



    except Exception as e:

        return f"خطأ في الصوت: {e}"