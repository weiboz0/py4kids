text = input().split()[0]
operators = []
top = 0
pieces = []
count = 0
postfix = ""
for ch in text:
    if ch == "+" or ch == "-" or ch == "*" or ch == "/" or ch == "^":
        if top == len(operators):
            operators.append(ch)
        else:
            operators[top] = ch
        top = top + 1
    elif ch == ")":
        top = top - 1
        op = operators[top]
        postfix = postfix + " " + op
        right = pieces[count - 1]
        left = pieces[count - 2]
        count = count - 2
        piece = op + " " + left + " " + right
        pieces[count] = piece
        count = count + 1
    elif ch != "(":
        postfix = postfix + " " + ch
        if count == len(pieces):
            pieces.append(ch)
        else:
            pieces[count] = ch
        count = count + 1
print(postfix[1:])
print(pieces[0])
