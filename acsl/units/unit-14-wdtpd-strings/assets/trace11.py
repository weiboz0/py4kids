S = "HANNAH AND ANNA"
c = 0
for j in range(len(S) - 1):
    if S[j:j + 2] == "AN":
        c = c + 1
print(c)
