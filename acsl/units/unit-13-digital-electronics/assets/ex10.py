def gate(name, x, y):
    if name == "BUFFER":
        answer = x
    elif name == "NOT":
        answer = 1 - x
    elif name == "AND" or name == "NAND":
        answer = x * y
    elif name == "OR" or name == "NOR":
        answer = max(x, y)
    else:
        answer = int(x != y)
    if name == "NAND" or name == "NOR" or name == "XNOR":
        answer = 1 - answer
    return answer


n = int(input())
for i in range(n):
    parts = input().split()
    x = int(parts[1])
    y = 0
    if len(parts) == 3:
        y = int(parts[2])
    print(gate(parts[0], x, y))
