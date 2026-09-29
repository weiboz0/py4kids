a = 6
b = -3
c = 0
count = 0
if a > 0 and b > 0:
    count = count + 1
if a > 0 or b > 0:
    count = count + 10
if not (c == 0) or a + b == 3:
    count = count + 100
if a > 5 or b > 5 and c > 5:
    count = count + 1000
if (a > 5 or b > 5) and c > 5:
    count = count + 10000
print(count)
