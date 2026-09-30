import sys


def beacons_placed(spots, gap):
    placed = 1
    last = spots[0]
    for spot in spots:
        if spot - last >= gap:
            placed = placed + 1
            last = spot
    return placed


data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
k = int(tokens[1])
spots = []
i = 0
while i < n:
    spots.append(int(tokens[2 + i]))
    i = i + 1
spots.sort()

lo = 1
hi = spots[n - 1] - spots[0]
while lo < hi:
    mid = (lo + hi + 1) // 2
    if beacons_placed(spots, mid) >= k:
        lo = mid
    else:
        hi = mid - 1
print(str(lo))
