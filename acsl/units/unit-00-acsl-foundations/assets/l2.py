count = 0
total = 0
largest = 0
value = int(input())
while value != 0:
    if count == 0:
        largest = value
    if value > largest:
        largest = value
    count = count + 1
    total = total + value
    value = int(input())
print(count, total, largest)
