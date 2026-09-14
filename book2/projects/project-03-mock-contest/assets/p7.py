import sys

data = sys.stdin.read()
n = int(data.split()[0])
used = []
build = 0
while build <= n:
    used.append(0)
    build = build + 1

def place(seat):
    if seat > n:
        return 1
    total = 0
    p = 1
    while p <= n:
        if used[p] == 0 and p != seat:
            used[p] = 1
            total = total + place(seat + 1)
            used[p] = 0
        p = p + 1
    return total

print(str(place(1)))
