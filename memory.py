import json
import os
import difflib
from datetime import datetime


# =========================================================
# ملف الذاكرة
# =========================================================

MEMORY_FILE = "memory.json"


# =========================================================
# تحميل الذاكرة
# =========================================================

def load_memory():

    if os.path.exists(MEMORY_FILE):

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    return data

        except Exception as e:

            print(
                "MEMORY LOAD ERROR:",
                e
            )

    return {}


# =========================================================
# حفظ الذاكرة
# =========================================================

def save_memory(data):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "MEMORY SAVE ERROR:",
            e
        )


# =========================================================
# تنظيف السؤال
# =========================================================

def normalize_question(question):

    if not question:
        return ""

    return " ".join(
        question.strip().lower().split()
    )


# =========================================================
# تعلم سؤال وجواب
# =========================================================

def learn(
    question,
    answer,
    source="ai",
    image_info=None
):

    if not question or not answer:
        return

    memory = load_memory()

    if "questions" not in memory:
        memory["questions"] = {}

    normalized = normalize_question(
        question
    )

    if not normalized:
        return

    memory["questions"][normalized] = {

        "question":
            question.strip(),

        "answer":
            answer,

        "source":
            source,

        "date":
            datetime.now().isoformat(),

        "image_info":
            image_info
    }

    save_memory(memory)


# =========================================================
# البحث عن إجابة سابقة
# =========================================================

def get_answer(
    question,
    similarity=True
):

    if not question:
        return None

    memory = load_memory()

    questions = memory.get(
        "questions",
        {}
    )

    if not questions:
        return None

    normalized = normalize_question(
        question
    )


    # =====================================================
    # مطابقة مباشرة
    # =====================================================

    saved = questions.get(
        normalized
    )

    if saved:

        # دعم الذاكرة القديمة
        if isinstance(saved, str):
            return saved

        if isinstance(saved, dict):
            return saved.get(
                "answer"
            )


    # =====================================================
    # البحث عن سؤال مشابه
    # =====================================================

    if similarity:

        saved_questions = list(
            questions.keys()
        )

        matches = difflib.get_close_matches(
            normalized,
            saved_questions,
            n=1,
            cutoff=0.82
        )

        if matches:

            matched_question = matches[0]

            saved = questions.get(
                matched_question
            )

            if isinstance(saved, str):
                return saved

            if isinstance(saved, dict):
                return saved.get(
                    "answer"
                )

    return None


# =========================================================
# الحصول على معلومات الذاكرة لسؤال
# =========================================================

def get_memory_entry(question):

    if not question:
        return None

    memory = load_memory()

    questions = memory.get(
        "questions",
        {}
    )

    normalized = normalize_question(
        question
    )

    entry = questions.get(
        normalized
    )

    if isinstance(entry, dict):
        return entry

    return None


# =========================================================
# اسم المستخدم
# =========================================================

def save_user_name(name):

    if not name:
        return

    memory = load_memory()

    memory["user_name"] = name.strip()

    save_memory(memory)


def get_user_name():

    memory = load_memory()

    return memory.get(
        "user_name"
    )


# =========================================================
# حفظ محادثة كاملة
# =========================================================

def save_conversation(
    title,
    messages
):

    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []

    conversation = {

        "title":
            title,

        "messages":
            messages,

        "date":
            datetime.now().isoformat()
    }

    memory["conversations"].append(
        conversation
    )

    save_memory(memory)


# =========================================================
# إضافة سؤال وجواب إلى آخر محادثة
# =========================================================

def add_conversation_message(
    question,
    answer,
    image_info=None
):

    if not question or not answer:
        return

    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []


    # =====================================================
    # إذا لم توجد محادثة، إنشاء محادثة جديدة
    # =====================================================

    if not memory["conversations"]:

        memory["conversations"].append({

            "title":
                "محادثة جديدة",

            "messages":
                [],

            "date":
                datetime.now().isoformat()
        })

    conversation = memory["conversations"][-1]

    if "messages" not in conversation:
        conversation["messages"] = []

    message = {

        "question":
            question,

        "answer":
            answer,

        "date":
            datetime.now().isoformat(),

        "image_info":
            image_info
    }

    conversation["messages"].append(
        message
    )


    # =====================================================
    # حفظ السؤال والجواب أيضًا في قاموس الأسئلة
    # =====================================================

    if "questions" not in memory:
        memory["questions"] = {}

    normalized = normalize_question(
        question
    )

    memory["questions"][normalized] = {

        "question":
            question,

        "answer":
            answer,

        "source":
            "conversation",

        "date":
            datetime.now().isoformat(),

        "image_info":
            image_info
    }

    save_memory(memory)


# =========================================================
# الحصول على جميع المحادثات
# =========================================================

def get_conversations():

    memory = load_memory()

    return memory.get(
        "conversations",
        []
    )


# =========================================================
# آخر محادثة
# =========================================================

def get_last_conversation():

    conversations = get_conversations()

    if conversations:
        return conversations[-1]

    return None


# =========================================================
# الحصول على آخر الأسئلة
# =========================================================

def get_recent_questions(
    limit=20
):

    memory = load_memory()

    questions = memory.get(
        "questions",
        {}
    )

    items = list(
        questions.items()
    )

    items.reverse()

    return items[:limit]


# =========================================================
# مراجعة الأسئلة والأجوبة السابقة
# =========================================================

def review_previous_questions(
    limit=20
):

    memory = load_memory()

    questions = memory.get(
        "questions",
        {}
    )

    if not questions:
        return []

    items = []

    for key, value in questions.items():

        if isinstance(value, str):

            items.append({

                "question":
                    key,

                "answer":
                    value
            })

        elif isinstance(value, dict):

            items.append({

                "question":
                    value.get(
                        "question",
                        key
                    ),

                "answer":
                    value.get(
                        "answer",
                        ""
                    ),

                "date":
                    value.get(
                        "date"
                    ),

                "image_info":
                    value.get(
                        "image_info"
                    )
            })

    items.reverse()

    return items[:limit]


# =========================================================
# مراجعة المحادثات السابقة
# =========================================================

def review_previous_conversations(
    limit=10
):

    conversations = get_conversations()

    if not conversations:
        return []

    return list(
        reversed(
            conversations[-limit:]
        )
    )


# =========================================================
# البحث في المحادثات السابقة
# =========================================================

def search_conversations(
    question,
    limit=5
):

    if not question:
        return []

    normalized = normalize_question(
        question
    )

    results = []

    conversations = get_conversations()

    for conversation in reversed(
        conversations
    ):

        messages = conversation.get(
            "messages",
            []
        )

        for message in reversed(
            messages
        ):

            old_question = normalize_question(
                message.get(
                    "question",
                    ""
                )
            )

            if not old_question:
                continue

            similarity = difflib.SequenceMatcher(
                None,
                normalized,
                old_question
            ).ratio()

            if similarity >= 0.70:

                results.append({

                    "question":
                        message.get(
                            "question"
                        ),

                    "answer":
                        message.get(
                            "answer"
                        ),

                    "date":
                        message.get(
                            "date"
                        ),

                    "image_info":
                        message.get(
                            "image_info"
                        ),

                    "similarity":
                        similarity
                })

                if len(results) >= limit:
                    return results

    return results


# =========================================================
# عدد الذكريات
# =========================================================

def memory_count():

    memory = load_memory()

    questions = memory.get(
        "questions",
        {}
    )

    return len(
        questions
    )


# =========================================================
# عدد المحادثات
# =========================================================

def conversation_count():

    memory = load_memory()

    conversations = memory.get(
        "conversations",
        []
    )

    return len(
        conversations
    )


# =========================================================
# مسح الذاكرة
# =========================================================

def clear_memory():

    save_memory({

        "questions": {},

        "conversations": [],

        "user_name": None
    })