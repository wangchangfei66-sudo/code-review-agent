API_KEY = "sk-demo-do-not-use-1234567890"


def add(a,b):
    print("debug add", a, b)
    return a+b


def divide(a, b):
    try:
        return a / b
    except Exception:
        pass


def run_expression(expr):
    return eval(expr)
