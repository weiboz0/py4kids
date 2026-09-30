S = input()
P = input()
m = len(P)
c = 0
first = -1
for j in range(len(S) - m + 1):
    if S[j:j + m] == P:
        c = c + 1
        if first == -1:
            first = j
print(c, first)
