parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = int(parts[2])
a, b = b, a
b, c = c, b + a
print(a, b, c)
