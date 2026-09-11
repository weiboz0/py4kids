import sys

data = sys.stdin.read()
values = data.split()
n = int(values[0])
quorum = int(values[1])
yes_count = 0
for i in range(n):
    if values[i + 2] == "YES":
        yes_count = yes_count + 1
if n >= quorum and yes_count * 2 > n:
    print("PASS")
else:
    print("FAIL")
