prev = 5
biggest = 0
where = 0
for k in range(1, 8):
    cur = (prev * 7 + k) % 23
    gap = abs(cur - prev)
    if gap >= biggest:
        biggest = gap
        where = k
    prev = cur
print(biggest, where)
