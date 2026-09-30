import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
values = []
i = 0
while i < n:
    values.append(int(tokens[1 + i]))
    i = i + 1

count = 0
i = 0
while i < n:
    j = i + 1
    while j < n:
        k = j + 1
        while k < n:
            if values[j] - values[i] == values[k] - values[j]:
                count = count + 1
            k = k + 1
        j = j + 1
    i = i + 1
print(str(count))
