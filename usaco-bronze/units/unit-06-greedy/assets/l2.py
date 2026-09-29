import sys

data = sys.stdin.read()
amount = int(data.strip())
coins = [25, 10, 5, 1]
coins.sort(reverse=True)
used = 0
for coin in coins:
    used = used + amount // coin
    amount = amount % coin
print(str(used))
