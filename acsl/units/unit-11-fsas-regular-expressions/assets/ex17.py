def read_tokens(p):
    tokens = []
    i = 0
    while i < len(p):
        if p[i] == "[":
            j = i
            while p[j] != "]":
                j = j + 1
            spec = p[i:j + 1]
            i = j + 1
        else:
            spec = p[i]
            i = i + 1
        mark = ""
        if i < len(p):
            if p[i] == "?" or p[i] == "+" or p[i] == "*":
                mark = p[i]
                i = i + 1
        tokens.append((spec, mark))
    return tokens


def in_class(body, c):
    k = 0
    while k < len(body):
        if k + 2 < len(body) and body[k + 1] == "-":
            if body[k] <= c and c <= body[k + 2]:
                return True
            k = k + 3
        else:
            if body[k] == c:
                return True
            k = k + 1
    return False


def fits(spec, c):
    if spec == ".":
        return True
    if len(spec) == 1:
        return spec == c
    body = spec[1:len(spec) - 1]
    if body[0] == "^":
        return not in_class(body[1:len(body)], c)
    return in_class(body, c)


def match(tokens, i, s, j):
    if i == len(tokens):
        return j == len(s)
    spec, mark = tokens[i]
    one = j < len(s) and fits(spec, s[j])
    if mark == "":
        return one and match(tokens, i + 1, s, j + 1)
    if mark == "?":
        if match(tokens, i + 1, s, j):
            return True
        return one and match(tokens, i + 1, s, j + 1)
    if mark == "*":
        if match(tokens, i + 1, s, j):
            return True
        return one and match(tokens, i, s, j + 1)
    if one:
        if match(tokens, i + 1, s, j + 1):
            return True
        return match(tokens, i, s, j + 1)
    return False


tokens = read_tokens(input())
n = int(input())
for k in range(n):
    word = input()
    if word == "-":
        word = ""
    if match(tokens, 0, word, 0):
        print("ACCEPT")
    else:
        print("REJECT")
