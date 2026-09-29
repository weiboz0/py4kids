def literal_value(literal, a, b, c, d):
    name = literal
    if literal[0] == "~":
        name = literal[1]
    if name == "A":
        value = a
    elif name == "B":
        value = b
    elif name == "C":
        value = c
    else:
        value = d
    if literal[0] == "~":
        value = 1 - value
    return value


def combine(op, left, right):
    if op == "XOR":
        return int(left != right)
    return int(left == right)


def expression_value(tokens, a, b, c, d):
    answer = 0
    chain = 0
    op = ""
    product = 1
    for token in tokens:
        if token == "+" or token == "XOR" or token == "XNOR":
            if op == "":
                chain = product
            else:
                chain = combine(op, chain, product)
            product = 1
            op = token
            if token == "+":
                if chain == 1:
                    answer = 1
                op = ""
        elif token != "*":
            if literal_value(token, a, b, c, d) == 0:
                product = 0
    return answer


tokens = input().split()
tokens.append("+")
found = 0
for a in range(2):
    for b in range(2):
        for c in range(2):
            for d in range(2):
                if expression_value(tokens, a, b, c, d) == 1:
                    found = found + 1
print(found)
