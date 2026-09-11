import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
frequencies = {}
best_value = int(parts[1])
best_frequency = 0
i = 0
while i < n:
    value = int(parts[i + 1])
    frequencies[value] = frequencies.get(value, 0) + 1
    frequency = frequencies[value]
    if frequency > best_frequency or frequency == best_frequency and value < best_value:
        best_value = value
        best_frequency = frequency
    i = i + 1
print(str(best_value))
