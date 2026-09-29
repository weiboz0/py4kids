total = 0
count = 0
value = int(input())
while value != 0:
    if value > count:
        total = total + value
    count = count + 1
    value = int(input())
print(count, total)
