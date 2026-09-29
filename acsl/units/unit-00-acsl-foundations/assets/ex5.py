evens = 0
odds = 0
value = int(input())
while value != 0:
    if value % 2 == 0:
        evens = evens + 1
    else:
        odds = odds + 1
    value = int(input())
print(evens, odds)
