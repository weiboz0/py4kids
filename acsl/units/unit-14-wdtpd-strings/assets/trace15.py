S = "STRESSEDDESERTS"
i = 0
j = len(S) - 1
steps = 0
while i < j and S[i] == S[j]:
    i = i + 1
    j = j - 1
    steps = steps + 1
print(steps, i, j)
