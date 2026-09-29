OPERATORS = ["+", "-", "*", "/", "^"]

stack = []
top = 0
for token in input().split():
    if token in OPERATORS:
        right = stack[top - 1]
        left = stack[top - 2]
        top = top - 2
        item = token + " " + left + " " + right
    else:
        item = token
    if top == len(stack):
        stack.append(item)
    else:
        stack[top] = item
    top = top + 1
print(stack[top - 1])
