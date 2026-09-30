OPERATORS = ["+", "-", "*", "/", "^"]


def apply(op, left, right):
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    return left ** right


def show(value):
    if value == int(value):
        return str(int(value))
    return str(value)


pairs = input().split()
letters = []
values = []
for i in range(0, len(pairs), 2):
    letters.append(pairs[i])
    values.append(int(pairs[i + 1]))

stack = []
top = 0
for token in input().split():
    if token in OPERATORS:
        right = stack[top - 1]
        left = stack[top - 2]
        top = top - 2
        value = apply(token, left, right)
    elif token in letters:
        k = 0
        while letters[k] != token:
            k = k + 1
        value = values[k]
    else:
        value = int(token)
    if top == len(stack):
        stack.append(value)
    else:
        stack[top] = value
    top = top + 1
print(show(stack[top - 1]))
