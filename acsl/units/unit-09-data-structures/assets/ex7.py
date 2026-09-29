kind = input()
n = int(input())

items = []
top = 0
head = 0
for step in range(n):
    parts = input().split()
    if parts[0] == "PUSH":
        if kind == "STACK":
            if top == len(items):
                items.append(parts[1])
            else:
                items[top] = parts[1]
            top = top + 1
        else:
            items.append(parts[1])
    elif kind == "STACK":
        if top == 0:
            print("NIL")
        else:
            top = top - 1
            print(items[top])
    else:
        if head == len(items):
            print("NIL")
        else:
            print(items[head])
            head = head + 1
