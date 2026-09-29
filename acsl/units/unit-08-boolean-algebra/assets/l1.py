def literal_value(literal, a, b, c):
    name = literal
    if literal[0] == "~":
        name = literal[1]
    if name == "A":
        value = a
    elif name == "B":
        value = b
    else:
        value = c
    if literal[0] == "~":
        value = 1 - value
    return value


def sop_value(tokens, a, b, c):
    answer = 0
    term = 1
    for token in tokens:
        if token == "+":
            if term == 1:
                answer = 1
            term = 1
        elif token != "*":
            if literal_value(token, a, b, c) == 0:
                term = 0
    if term == 1:
        answer = 1
    return answer


text = input()
tokens = text.split()
c_values = 1
if "C" in text:
    c_values = 2
for a in range(2):
    for b in range(2):
        for c in range(c_values):
            row = str(a) + " " + str(b)
            if c_values == 2:
                row = row + " " + str(c)
            print(row + " : " + str(sop_value(tokens, a, b, c)))
