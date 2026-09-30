A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
S = "ZEBRA"
T = ""
for j in range(len(S)):
    k = 0
    while A[k] != S[j]:
        k = k + 1
    T = T + A[(k + j) % 26]
print(T, T[1:4])
