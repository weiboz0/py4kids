S = input()
out = ""
for j in range(len(S)):
    if j % 2 == 0:
        out = out + S[j]
    else:
        out = S[j] + out
print(out)
