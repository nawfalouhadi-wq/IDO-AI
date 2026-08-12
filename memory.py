import json
import os
import difflib
import uuid
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
        str(question)
        .strip()
        .lower()
        .split()
    )


# =========================================================
# إنشاء معرف محادثة
# =========================================================

def create_conversation_id():
    return (
        "chat_"
        + uuid.uuid4().hex
    )


# =========================================================
# العثور على محادثة بالمعرف
# =========================================================

def get_conversation_by_id(
    conversation_id
):

    if not conversation_id:
        return None

    conversations = get_conversations()

    for conversation in conversations:

        if (
            isinstance(conversation, dict)
            and conversation.get("id")
            == conversation_id
        ):
            return conversation

    return None


# =========================================================
# إنشاء محادثة جديدة في الذاكرة
# =========================================================

def create_conversation(
    title="محادثة جديدة"
):

    conversation = {

        "id":
            create_conversation_id(),

        "title":
            title or "محادثة جديدة",

        "messages":
            [],

        "date":
            datetime.now().isoformat()
    }

    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []

    memory["conversations"].append(
        conversation
    )

    save_memory(memory)

    return conversation


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
            str(question).strip(),

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

    memory["user_name"] = (
        str(name).strip()
    )

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
    messages,
    conversation_id=None
):

    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []

    conversation = {

        "id":
            conversation_id
            or create_conversation_id(),

        "title":
            title or "محادثة جديدة",

        "messages":
            messages
            if isinstance(messages, list)
            else [],

        "date":
            datetime.now().isoformat()
    }

    memory["conversations"].append(
        conversation
    )

    save_memory(memory)

    return conversation["id"]


# =========================================================
# إضافة رسالة إلى محادثة محددة
# =========================================================

def add_conversation_message(
    question,
    answer,
    image_info=None,
    conversation_id=None
):

    if not question or not answer:
        return None

    memory = load_memory()

    if "conversations" not in memory:
        memory["conversations"] = []

    # =====================================================
    # العثور على المحادثة المطلوبة
    # =====================================================

    conversation = None

    if conversation_id:

        for item in memory["conversations"]:

            if (
                isinstance(item, dict)
                and item.get("id")
                == conversation_id
            ):

                conversation = item
                break

    # =====================================================
    # التوافق مع النظام القديم
    # =====================================================

    if conversation is None:

        if memory["conversations"]:

            conversation = (
                memory["conversations"][-1]
            )

        else:

            conversation = {

                "id":
                    conversation_id
                    or create_conversation_id(),

                "title":
                    "محادثة جديدة",

                "messages":
                    [],

                "date":
                    datetime.now().isoformat()
            }

            memory["conversations"].append(
                conversation
            )

    # =====================================================
    # ضمان وجود البيانات الأساسية
    # =====================================================

    if not conversation.get("id"):

        conversation["id"] = (
            conversation_id
            or create_conversation_id()
        )

    if "messages" not in conversation:
        conversation["messages"] = []

    # =====================================================
    # إضافة الرسالة
    # =====================================================

    message = {

        "question":
            str(question).strip(),

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
    # تحديث عنوان المحادثة
    # =====================================================

    if (
        not conversation.get("title")
        or conversation.get("title")
        == "محادثة جديدة"
    ):

        conversation["title"] = (
            str(question).strip()[:60]
            or "محادثة جديدة"
        )

    conversation["date"] = (
        datetime.now().isoformat()
    )

    # =====================================================
    # حفظ السؤال والجواب في الذاكرة العامة
    # =====================================================

    if "questions" not in memory:
        memory["questions"] = {}

    normalized = normalize_question(
        question
    )

    if normalized:

        memory["questions"][normalized] = {

            "question":
                str(question).strip(),

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

    return conversation["id"]


# =========================================================
# إضافة رسالة عامة إلى محادثة
# =========================================================

def append_message(
    conversation_id,
    role,
    text,
    image=None
):

    if not conversation_id:
        return False

    memory = load_memory()

    conversations = memory.get(
        "conversations",
        []
    )

    for conversation in conversations:

        if (
            not isinstance(
                conversation,
                dict
            )
        ):
            continue

        if (
            conversation.get("id")
            != conversation_id
        ):
            continue

        if "messages" not in conversation:
            conversation["messages"] = []

        conversation["messages"].append({

            "role":
                role,

            "text":
                text or "",

            "image":
                image,

            "date":
                datetime.now().isoformat()
        })

        conversation["date"] = (
            datetime.now().isoformat()
        )

        save_memory(memory)

        return True

    return False


# =========================================================
# الحصول على جميع المحادثات
# =========================================================

def get_conversations():

    memory = load_memory()

    conversations = memory.get(
        "conversations",
        []
    )

    if not isinstance(
        conversations,
        list
    ):
        return []

    # =====================================================
    # ترقية المحادثات القديمة تلقائيًا
    # =====================================================

    changed = False

    for conversation in conversations:

        if not isinstance(
            conversation,
            dict
        ):
            continue

        if not conversation.get("id"):

            conversation["id"] = (
                create_conversation_id()
            )

            changed = True

        if "messages" not in conversation:

            conversation["messages"] = []

            changed = True

    if changed:

        memory["conversations"] = conversations
        save_memory(memory)

    return conversations


# =========================================================
# آخر محادثة
# =========================================================

def get_last_conversation():

    conversations = get_conversations()

    if conversations:
        return conversations[-1]

    return None


# =========================================================
# آخر محادثة بالمعرف
# =========================================================

def get_conversation_context(
    conversation_id,
    limit=12
):

    conversation = (
        get_conversation_by_id(
            conversation_id
        )
    )

    if not conversation:
        return []

    messages = conversation.get(
        "messages",
        []
    )

    if not isinstance(
        messages,
        list
    ):
        return []

    return messages[-max(
        1,
        int(limit)
    ):]


# =========================================================
# إنشاء نص سياق للمحادثة
# =========================================================

def build_conversation_context(
    conversation_id,
    limit=12
):

    messages = (
        get_conversation_context(
            conversation_id,
            limit
        )
    )

    if not messages:
        return ""

    context = []

    for message in messages:

        if not isinstance(
            message,
            dict
        ):
            continue

        # =================================================
        # النظام الجديد role/text
        # =================================================

        if "role" in message:

            role = message.get(
                "role",
                "user"
            )

            text = message.get(
                "text",
                ""
            )

            if text:

                if role == "assistant":

                    context.append(
                        "Aido AI: "
                        + str(text)
                    )

                else:

                    context.append(
                        "المستخدم: "
                        + str(text)
                    )

            continue

        # =================================================
        # النظام القديم question/answer
        # =================================================

        question = message.get(
            "question",
            ""
        )

        answer = message.get(
            "answer",
            ""
        )

        if question:

            context.append(
                "المستخدم: "
                + str(question)
            )

        if answer:

            context.append(
                "Aido AI: "
                + str(answer)
            )

    return "\n".join(
        context
    )


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

        if isinstance(
            value,
            str
        ):

            items.append({

                "question":
                    key,

                "answer":
                    value
            })

        elif isinstance(
            value,
            dict
        ):

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

    conversations = (
        get_conversations()
    )

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

    conversations = (
        get_conversations()
    )

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

            if not isinstance(
                message,
                dict
            ):
                continue

            old_question = (
                normalize_question(
                    message.get(
                        "question",
                        ""
                    )
                )
            )

            if not old_question:
                continue

            similarity = (
                difflib.SequenceMatcher(
                    None,
                    normalized,
                    old_question
                ).ratio()
            )

            if similarity >= 0.70:

                results.append({

                    "conversation_id":
                        conversation.get(
                            "id"
                        ),

                    "conversation_title":
                        conversation.get(
                            "title"
                        ),

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