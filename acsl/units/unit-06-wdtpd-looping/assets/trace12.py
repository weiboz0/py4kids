c = 0
t = 0
for i in range(1, 6):
    for j in range(i, 6):
        c = c + 1
        if (i + j) % 3 == 0:
            t = t + i * j
print(c, t)
