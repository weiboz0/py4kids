def div(x, y):
    q = abs(x) // abs(y)
    if x * y < 0:
        q = -q
    return q


n = int(input())
acc = 0
for k in range(n):
    parts = input().split()
    op = parts[0]
    loc = parts[1]
    v = int(loc[1:len(loc)])
    if op == "LOAD":
        acc = v
    elif op == "ADD":
        acc = acc + v
    elif op == "SUB":
        acc = acc - v
    elif op == "MULT":
        acc = acc * v
    elif op == "DIV":
        acc = div(acc, v)
    print(acc)
