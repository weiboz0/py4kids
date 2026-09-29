a = 3
s = 0
for k in range(1, 7):
    s = s + abs(a - k * 2)
    a = a + 1
print(s)
