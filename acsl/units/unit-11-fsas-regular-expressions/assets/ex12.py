def match(p, i, s, j):
    if i == len(p):
        return j == len(s)
    fits = j < len(s) and s[j] == p[i]
    mark = ""
    if i + 1 < len(p):
        if p[i + 1] == "?" or p[i + 1] == "+" or p[i + 1] == "*":
            mark = p[i + 1]
    if mark == "":
        return fits and match(p, i + 1, s, j + 1)
    if mark == "?":
        if match(p, i + 2, s, j):
            return True
        return fits and match(p, i + 2, s, j + 1)
    if mark == "*":
        if match(p, i + 2, s, j):
            return True
        return fits and match(p, i, s, j + 1)
    if fits:
        if match(p, i + 2, s, j + 1):
            return True
        return match(p, i, s, j + 1)
    return False


pattern = input()
n = int(input())
for k in range(n):
    word = input()
    if word == "-":
        word = ""
    if match(pattern, 0, word, 0):
        print("ACCEPT")
    else:
        print("REJECT")
