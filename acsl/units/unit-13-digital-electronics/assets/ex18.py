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


def run(lines, value):
    last = ""
    for line in lines:
        w = words(line)
        x = value[w[2]]
        y = 0
        if len(w) == 4:
            y = value[w[3]]
        value[w[0]] = gate(w[1], x, y)
        last = w[0]
    return value[last]


g = int(input())
names = words(input())
lines = []
for i in range(g):
    lines.append(input())
want = int(input())

k = len(names) - 1
total = 1
for i in range(k):
    total = total * 2

found = 0
answer = ""
for row in range(total):
    value = {}
    rest = row
    for i in range(k, 0, -1):
        value[names[i]] = rest % 2
        rest = rest // 2
    if run(lines, value) == want:
        if found > 0:
            answer = answer + ", "
        text = "("
        for i in range(1, k + 1):
            if i > 1:
                text = text + ","
            text = text + str(value[names[i]])
        answer = answer + text + ")"
        found = found + 1
print(found)
if found == 0:
    print("NONE")
else:
    print(answer)
