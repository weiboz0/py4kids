S = input()
best = 1
bestc = S[0]
run = 1
for j in range(1, len(S)):
    if S[j] == S[j - 1]:
        run = run + 1
    else:
        run = 1
    if run > best:
        best = run
        bestc = S[j]
print(bestc, best)
