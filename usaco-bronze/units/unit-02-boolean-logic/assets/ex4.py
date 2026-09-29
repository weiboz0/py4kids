import sys

data = sys.stdin.read()
values = data.split()
n = int(values[0])
every_check_passed = True
for i in range(n):
    if int(values[i + 1]) == 0:
        every_check_passed = False
if every_check_passed:
    print("YES")
else:
    print("NO")
