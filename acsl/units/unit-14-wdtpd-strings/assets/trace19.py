O = "ABCDEFGHIJ"
S = O
k = 0
first = ""
done = 0
while done == 0:
    h = len(S) // 2
    L = S[:h]
    R = S[len(S) - h:]
    S = ""
    for j in range(h):
        S = S + R[j] + L[j]
    k = k + 1
    if k == 1:
        first = S
    if S == O:
        done = 1
print(k, first)
