import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
seen = set()
answer = "NONE"
i = 0
while i < n:
    code = parts[i + 1]
    if answer == "NONE" and code in seen:
        answer = code
    seen.add(code)
    i = i + 1
print(answer)
