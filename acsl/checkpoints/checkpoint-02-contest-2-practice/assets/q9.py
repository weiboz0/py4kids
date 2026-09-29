tokens = input().split()
stack = []
top = 0
deepest = 0
for token in tokens:
    if token == "+" or token == "-" or token == "*":
        right = stack[top - 1]
        left = stack[top - 2]
        top = top - 2
        if token == "+":
            value = left + right
        elif token == "-":
            value = left - right
        else:
            value = left * right
    else:
        value = int(token)
    if top == len(stack):
        stack.append(value)
    else:
        stack[top] = value
    top = top + 1
    if top > deepest:
        deepest = top
print(str(stack[0]) + " " + str(deepest))
