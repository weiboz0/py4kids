import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
target = int(tokens[1])
seen = {}
checks = 0
found = False

for position in range(n):
    number = int(tokens[position + 2])
    needed = target - number
    checks = checks + 1
    if needed in seen:
        found = True
    seen[number] = True

answer = "NO"
if found:
    answer = "YES"
print(answer + "\nPartner checks: " + str(checks))
