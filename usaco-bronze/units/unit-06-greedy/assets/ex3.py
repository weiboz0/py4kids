import sys

data = sys.stdin.read()
parts = data.split()
amount = int(parts[0])
coins = [25, 10, 5, 1]
coins.sort(reverse=True)
coin_count = 0
i = 0
while i < 4:
    coin_count = coin_count + amount // coins[i]
    amount = amount % coins[i]
    i = i + 1
print(str(coin_count))
