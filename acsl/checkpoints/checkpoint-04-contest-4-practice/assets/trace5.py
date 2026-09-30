S = "WATERMELON"
T = S[:1]
for j in range(1, 4):  # ACSL: FOR j = 1 TO 3
    T = T + S[j:j + 2] + S[len(S) - j:]
print(T, len(T))
