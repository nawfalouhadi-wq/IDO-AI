import ast
import math
import operator
import re


# =========================================================
# Calculator - Aido AI
# =========================================================

MAX_EXPRESSION_LENGTH = 500


# =========================================================
# العمليات المسموح بها
# =========================================================

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


# =========================================================
# الدوال الرياضية
# =========================================================

FUNCTIONS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
}


CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


# =========================================================
# تنظيف التعبير
# =========================================================

def clean_expression(expression):

    if not isinstance(expression, str):
        return None

    expression = expression.strip()

    if not expression:
        return None

    if len(expression) > MAX_EXPRESSION_LENGTH:
        return None

    # السماح بعلامة الضرب ×
    expression = expression.replace("×", "*")

    # السماح بعلامة القسمة ÷
    expression = expression.replace("÷", "/")

    # السماح بالفاصلة العشرية العربية
    expression = expression.replace("،", ".")

    # إزالة المسافات
    expression = expression.replace(" ", "")

    return expression


# =========================================================
# التحقق من الأرقام الكبيرة والخطرة
# =========================================================

def validate_number(value):

    if not math.isfinite(value):
        raise ValueError(
            "النتيجة غير محدودة."
        )

    if abs(value) > 10**100:
        raise ValueError(
            "الرقم الناتج كبير جدًا."
        )

    return value


# =========================================================
# تقييم AST بأمان
# =========================================================

def evaluate_node(node):

    # -----------------------------------------------------
    # رقم
    # -----------------------------------------------------

    if isinstance(node, ast.Constant):

        if isinstance(
            node.value,
            (int, float)
        ) and not isinstance(
            node.value,
            bool
        ):

            return validate_number(
                node.value
            )

        raise ValueError(
            "قيمة غير مسموحة."
        )


    # -----------------------------------------------------
    # ثابت رياضي
    # -----------------------------------------------------

    if isinstance(node, ast.Name):

        if node.id in CONSTANTS:

            return CONSTANTS[node.id]

        raise ValueError(
            "ثابت غير مسموح."
        )


    # -----------------------------------------------------
    # عملية حسابية
    # -----------------------------------------------------

    if isinstance(
        node,
        ast.BinOp
    ):

        if type(node.op) not in BINARY_OPERATORS:
            raise ValueError(
                "عملية غير مسموحة."
            )

        left = evaluate_node(
            node.left
        )

        right = evaluate_node(
            node.right
        )

        # حماية من الأسس الضخمة
        if isinstance(
            node.op,
            ast.Pow
        ):

            if abs(right) > 1000:
                raise ValueError(
                    "الأس غير مسموح أن يكون كبيرًا جدًا."
                )

        operation = BINARY_OPERATORS[
            type(node.op)
        ]

        result = operation(
            left,
            right
        )

        return validate_number(
            result
        )


    # -----------------------------------------------------
    # عملية أحادية
    # -----------------------------------------------------

    if isinstance(
        node,
        ast.UnaryOp
    ):

        if type(node.op) not in UNARY_OPERATORS:
            raise ValueError(
                "عملية غير مسموحة."
            )

        value = evaluate_node(
            node.operand
        )

        result = UNARY_OPERATORS[
            type(node.op)
        ](value)

        return validate_number(
            result
        )


    # -----------------------------------------------------
    # الدوال الرياضية
    # -----------------------------------------------------

    if isinstance(
        node,
        ast.Call
    ):

        if not isinstance(
            node.func,
            ast.Name
        ):

            raise ValueError(
                "دالة غير مسموحة."
            )

        function_name = node.func.id

        if function_name not in FUNCTIONS:
            raise ValueError(
                "هذه الدالة غير مسموحة."
            )

        if node.keywords:
            raise ValueError(
                "المعاملات المسماة غير مسموحة."
            )

        arguments = [
            evaluate_node(argument)
            for argument in node.args
        ]

        function = FUNCTIONS[
            function_name
        ]

        result = function(
            *arguments
        )

        return validate_number(
            result
        )


    raise ValueError(
        "تعبير غير مسموح."
    )


# =========================================================
# الحساب الرئيسي
# =========================================================

def calculate(expression):

    try:

        expression = clean_expression(
            expression
        )

        if expression is None:
            return None

        # -------------------------------------------------
        # منع بعض الصيغ غير الرياضية
        # -------------------------------------------------

        if re.search(
            r"[A-Za-z_]",
            expression
        ):

            # السماح فقط بأسماء الدوال والثوابت المعروفة
            names = re.findall(
                r"[A-Za-z_][A-Za-z0-9_]*",
                expression
            )

            allowed_names = set(
                FUNCTIONS.keys()
            ) | set(
                CONSTANTS.keys()
            )

            if any(
                name not in allowed_names
                for name in names
            ):

                return None


        # -------------------------------------------------
        # تحليل التعبير بدون eval
        # -------------------------------------------------

        tree = ast.parse(
            expression,
            mode="eval"
        )


        # -------------------------------------------------
        # الحساب
        # -------------------------------------------------

        result = evaluate_node(
            tree.body
        )


        # -------------------------------------------------
        # تنسيق النتيجة
        # -------------------------------------------------

        if isinstance(
            result,
            float
        ):

            if result.is_integer():

                return int(result)

            return round(
                result,
                12
            )

        return result


    except (
        ZeroDivisionError,
        ValueError,
        OverflowError,
        TypeError,
        SyntaxError,
        MemoryError
    ):

        return None

    except Exception:

        return None


# =========================================================
# اختبار الآلة الحاسبة
# =========================================================

if __name__ == "__main__":

    tests = [

        "2 + 2",

        "10 * 5",

        "100 / 4",

        "2 ** 10",

        "sqrt(144)",

        "pi * 2",

        "sin(pi / 2)",

        "log10(1000)",

        "5 + 3 * 2",

        "(10 + 5) / 3",

        "10 % 3",

        "floor(4.9)",

        "ceil(4.1)",

        "round(3.14159265, 2)",

    ]

    for expression in tests:

        print(
            f"{expression} = "
            f"{calculate(expression)}"
        )