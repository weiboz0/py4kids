S = "CHOCOLATE"
T = ""
while len(S) > 1:
    T = T + S[:1]
    S = S[len(S) - (len(S) - 2):]
print(T + S)
