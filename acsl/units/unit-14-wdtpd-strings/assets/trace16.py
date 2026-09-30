S = "WORDGAME"
T = ""
for j in range(0, len(S), 2):
    P = S[j:j + 2]
    if P[0] > P[1]:
        T = T + P[1] + P[0]
    else:
        T = T + P
print(T)
