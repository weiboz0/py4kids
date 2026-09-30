S = "STRUCTURES"
big = S[0]
where = 0
late = 0
for j in range(len(S)):
    if S[j] > big:
        big = S[j]
        where = j
    if S[j] >= "N":
        late = late + 1
print(big, where, late)
