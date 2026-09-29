kind = input()
tokens = input().split()

items = []
top = 0
head = 0
i = 0
while i < len(tokens):
    if tokens[i] == "PUSH":
        value = tokens[i + 1]
        if kind == "STACK":
            if top == len(items):
                items.append(value)
            else:
                items[top] = value
            top = top + 1
        else:
            items.append(value)
        line = "PUSH " + value + " :"
        i = i + 2
    else:
        if kind == "STACK":
            if top == 0:
                popped = "NIL"
            else:
                top = top - 1
                popped = items[top]
        else:
            if head == len(items):
                popped = "NIL"
            else:
                popped = items[head]
                head = head + 1
        line = "POP -> " + popped + " :"
        i = i + 1
    if kind == "STACK":
        for k in range(top):
            line = line + " " + items[k]
    else:
        for k in range(head, len(items)):
            line = line + " " + items[k]
    print(line)
