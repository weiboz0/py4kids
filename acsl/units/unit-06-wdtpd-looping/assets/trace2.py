total = 0
count = 0
for k in range(3, 30, 4):
    if k % 3 == 0:
        total = total + k
    else:
        count = count + 1
print(total, count)
