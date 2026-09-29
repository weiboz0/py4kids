parts = input().split()
hours = int(parts[0])
day = int(parts[1])
if day == 6 or day == 7:
    fee = 5
elif hours <= 2:
    fee = 0
elif hours <= 5:
    fee = (hours - 2) * 3
else:
    fee = 9 + (hours - 5) * 4
if fee > 20:
    fee = 20
print(fee)
