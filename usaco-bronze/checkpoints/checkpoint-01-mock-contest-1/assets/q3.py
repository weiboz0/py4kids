import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
prices = []
i = 0
while i < n:
    prices.append(int(parts[i + 1]))
    i = i + 1

smallest = prices[0]
best_gain = 0
i = 1
while i < n:
    gain = prices[i] - smallest
    if gain > best_gain:
        best_gain = gain
    if prices[i] < smallest:
        smallest = prices[i]
    i = i + 1
print(str(best_gain))
