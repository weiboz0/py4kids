import sys

data = sys.stdin.read()
expression = data.split()[0]

def evaluate(start, end):
    if expression[start] != "(":
        return int(expression[start:end])

    depth = 0
    operator_index = start + 1
    i = start + 1
    while i < end - 1:
        character = expression[i]
        if character == "(":
            depth = depth + 1
        elif character == ")":
            depth = depth - 1
        elif depth == 0:
            if character == "+" or character == "-" or character == "*":
                operator_index = i
        i = i + 1

    left = evaluate(start + 1, operator_index)
    right = evaluate(operator_index + 1, end - 1)
    operator = expression[operator_index]
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    return left * right

print(str(evaluate(0, len(expression))))
