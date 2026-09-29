def match(p, i, s, j):
    if i == len(p):
        return j == len(s)
    fits = j < len(s) and s[j] == p[i]
    if i + 1 < len(p) and p[i + 1] == "*":
        if match(p, i + 2, s, j):
            return True
        return fits and match(p, i, s, j + 1)
    return fits and match(p, i + 1, s, j + 1)


pattern = input()
word = input()
if match(pattern, 0, word, 0):
    print("ACCEPT")
else:
    print("REJECT")
