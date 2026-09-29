total = 0
for k in range(20, 0, -3):
    if k % 2 == 0:
        total = total + k
    else:
        total = total - 1
print(total)
