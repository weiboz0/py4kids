A = [4, 9, 2, 9, 1, 2]
big = A[0]
bpos = 0
small = A[0]
spos = 0
for i in range(1, 6):
    if A[i] >= big:
        big = A[i]
        bpos = i
    if A[i] < small:
        small = A[i]
        spos = i
print(bpos, spos, big - small)
