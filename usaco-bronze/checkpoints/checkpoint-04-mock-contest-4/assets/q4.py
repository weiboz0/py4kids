import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
target = int(tokens[1])
prices = []
i = 0
while i < n:
    prices.append(int(tokens[2 + i]))
    i = i + 1
prices = sorted(prices)
lo = 0
hi = n - 1
answer = "NO"
while lo < hi and answer == "NO":
    total = prices[lo] + prices[hi]
    if total == target:
        answer = "YES"
    elif total < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(answer)
