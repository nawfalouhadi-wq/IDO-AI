import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

session = requests.Session()


def ask_ollama(message):

    try:

        if not message.strip():
            return "اكتب سؤالًا أولًا."


        response = session.post(

            OLLAMA_URL,

            json={

                "model": "llama3.1:8b",

                "prompt": message,

                "stream": False,

                "keep_alive": "30m",

                "options": {

                    "num_predict": 40,

                    "temperature": 0.3,

                    "top_p": 0.7,

                    "num_ctx": 1024,

                    "repeat_penalty": 1.05

                }

            },

            timeout=45

        )


        response.raise_for_status()


        data = response.json()


        answer = data.get("response", "").strip()


        if answer:
            return answer

        return "لم أجد إجابة."


    except requests.exceptions.Timeout:

        return "⏳ تأخر الرد."


    except Exception as e:

        return f"خطأ: {e}"