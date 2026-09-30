S = input()
T = ""
for j in range(len(S)):
    if S[j] != " ":
        T = T + S[j]
R = ""
for j in range(len(T)):
    R = T[j] + R
if T == R:
    print("YES", len(T))
else:
    print("NO", len(T))
