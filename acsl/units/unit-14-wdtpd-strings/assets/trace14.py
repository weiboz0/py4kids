S = "ABCABCAB"
c = 0
b = 0
for k in range(1, len(S)):
    if S[:k] == S[len(S) - k:]:
        c = c + 1
        b = k
print(c, b)
