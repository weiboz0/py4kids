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


name = input()
if name == "BUFFER" or name == "NOT":
    for x in range(2):
        print(str(x) + " : " + str(gate(name, x, 0)))
else:
    for x in range(2):
        for y in range(2):
            print(str(x) + " " + str(y) + " : " + str(gate(name, x, y)))
