import sys

data = sys.stdin.read()
parts = data.split()
b = int(parts[0])
n = int(parts[1])
banned = set()
i = 0
while i < b:
    banned.add(parts[i + 2])
    i = i + 1
submitted = set()
i = 0
while i < n:
    submitted.add(parts[b + i + 2])
    i = i + 1
for code in banned:
    submitted.discard(code)
print(str(len(submitted)))
