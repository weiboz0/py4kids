import sys

data = sys.stdin.read()
parts = data.split()
coin_count = int(parts[0])
target = int(parts[1])
coins = []
i = 0
while i < coin_count:
    coins.append(int(parts[i + 2]))
    i = i + 1

def search(index, total, path):
    if index == coin_count:
        if total == target:
            return 1
        return 0

    ways = 0
    coin_total = total
    coin_amount = 0
    while coin_total <= target:
        ways = ways + search(index + 1, coin_total, path + [coin_amount])
        coin_amount = coin_amount + 1
        coin_total = coin_total + coins[index]
    return ways

print(str(search(0, 0, [])))
