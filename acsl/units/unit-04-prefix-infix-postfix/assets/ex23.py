OPERATORS = ["+", "-", "*", "/", "^"]

tokens = input().split()
stack = []
top = 0
for i in range(len(tokens) - 1, -1, -1):
    token = tokens[i]
    if token in OPERATORS:
        left = stack[top - 1]
        right = stack[top - 2]
        top = top - 2
        item = left + " " + right + " " + token
    else:
        item = token
    if top == len(stack):
        stack.append(item)
    else:
        stack[top] = item
    top = top + 1
print(stack[top - 1])
