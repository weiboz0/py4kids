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

count = 0
i = 0
while i < n - 2:
    j = i + 1
    while j < n - 1:
        k = j + 1
        while k < n:
            if values[i] + values[j] + values[k] == target:
                count = count + 1
            k = k + 1
        j = j + 1
    i = i + 1
print(str(count))
