S = "LEVELED"
c = 0
for a in range(len(S) - 1):
    for b in range(a + 1, len(S)):
        T = S[a:b + 1]
        R = ""
        for k in range(len(T)):
            R = T[k] + R
        if T == R:
            c = c + 1
print(c)
