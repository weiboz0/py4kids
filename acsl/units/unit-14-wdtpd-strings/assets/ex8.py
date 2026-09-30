S = input()
T = ""
v = 0
for j in range(len(S)):
    c = S[j]
    if c == "A" or c == "E" or c == "I" or c == "O" or c == "U":
        v = v + 1
    else:
        T = T + c
print(T, v)
