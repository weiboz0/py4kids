parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = int(parts[2])
t = int(parts[3])
ways = 0
for x in range(t // a + 1):
    for y in range(t // b + 1):
        rest = t - a * x - b * y
        if rest >= 0:
            if rest % c == 0:
                ways = ways + 1
print(ways)
