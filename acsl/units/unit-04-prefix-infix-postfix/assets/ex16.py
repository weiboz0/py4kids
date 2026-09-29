OPERATORS = ["+", "-", "*", "/", "^"]


def apply(op, left, right):
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left // right
    return left ** right


stack = []
top = 0
for token in input().split():
    if token in OPERATORS:
        right = stack[top - 1]
        left = stack[top - 2]
        top = top - 2
        value = apply(token, left, right)
    else:
        value = int(token)
    if top == len(stack):
        stack.append(value)
    else:
        stack[top] = value
    top = top + 1
print(stack[top - 1])
