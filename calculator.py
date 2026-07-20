def calculate(expression):
    try:
        allowed = "0123456789+-*/(). "

        for char in expression:
            if char not in allowed:
                return None

        return eval(expression)

    except:
        return None