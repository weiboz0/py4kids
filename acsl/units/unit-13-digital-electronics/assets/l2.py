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


def words(line):
    result = []
    word = ""
    for ch in line + " ":
        if ch in " =(),":
            if word != "":
                result.append(word)
            word = ""
        else:
            word = word + ch
    return result


g = int(input())
names = words(input())
lines = []
for i in range(g):
    lines.append(input())
bits = input().split()

value = {}
for i in range(1, len(names)):
    value[names[i]] = int(bits[i - 1])
last = ""
for line in lines:
    w = words(line)
    x = value[w[2]]
    y = 0
    if len(w) == 4:
        y = value[w[3]]
    value[w[0]] = gate(w[1], x, y)
    last = w[0]
print(value[last])
