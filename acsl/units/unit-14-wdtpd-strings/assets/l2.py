S = input()
R = ""
for j in range(len(S)):
    R = S[j] + R
if R == S:
    print(R, "YES")
else:
    print(R, "NO")
