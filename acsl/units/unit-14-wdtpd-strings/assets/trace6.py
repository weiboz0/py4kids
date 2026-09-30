S = "STRAWBERRY"
R = ""
for j in range(len(S)):
    R = S[j] + R
print(R[:3] + R[len(R) - 3:])
