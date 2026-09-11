import sys

data = sys.stdin.read()
values = data.split()
n = int(values[0])
x_count = 0
has_dissenter = False
for i in range(n):
    if values[i + 1] == "X":
        x_count = x_count + 1
    else:
        has_dissenter = True
if x_count * 2 > n and has_dissenter:
    print("YES")
else:
    print("NO")
