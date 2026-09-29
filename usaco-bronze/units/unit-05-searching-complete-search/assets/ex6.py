import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
values = []
i = 0
while i < n:
    values.append(int(parts[i + 2]))
    i = i + 1
answer = "NO"
i = 0
while i < n - 2 and answer == "NO":
    j = i + 1
    while j < n - 1 and answer == "NO":
        k = j + 1
        while k < n and answer == "NO":
            if values[i] + values[j] + values[k] == target:
                answer = "YES"
            k = k + 1
        j = j + 1
    i = i + 1
print(answer)
