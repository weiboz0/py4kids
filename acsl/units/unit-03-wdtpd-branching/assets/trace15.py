S = "ACSL CONTEST"
R = ""
for j in range(len(S) - 1, -1, -1):
    R = R + S[j]
# ACSL R[:4] = first 4; S[5:7] = positions 5 through 7; R[3:] = last 3
T = R[:4] + S[5:8] + R[len(R) - 3:]
print(T)
