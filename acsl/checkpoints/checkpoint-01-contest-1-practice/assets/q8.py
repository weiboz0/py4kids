n = int(input())
base = 2
found = False
while not found:
    digit = n % base
    rest = n
    count = 0
    same = True
    while rest > 0:
        if rest % base != digit:
            same = False
        rest = rest // base
        count = count + 1
    if same:
        found = True
    else:
        base = base + 1
print(str(base) + " " + str(digit) + " " + str(count))
