import math

total = 0
for n in range(1, 30, 4):
    root = math.sqrt(n)
    if root == math.floor(root):
        total = total + n
    else:
        total = total - math.floor(root)
print(total, math.sqrt(total + 32))
