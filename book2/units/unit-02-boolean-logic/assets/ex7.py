import sys

data = sys.stdin.read()
values = data.split()
n = int(values[0])
found_positive = False
for i in range(n):
    token = values[i + 1]
    if token != "SKIP" and int(token) > 0:
        found_positive = True
if found_positive:
    print("YES")
else:
    print("NO")
