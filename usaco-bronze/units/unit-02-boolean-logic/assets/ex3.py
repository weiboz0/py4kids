import sys

data = sys.stdin.read()
values = data.split()
n = int(values[0])
found_one = False
for i in range(n):
    if int(values[i + 1]) == 1:
        found_one = True
if found_one:
    print("YES")
else:
    print("NO")
