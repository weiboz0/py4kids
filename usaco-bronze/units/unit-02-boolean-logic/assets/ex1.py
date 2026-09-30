import sys

data = sys.stdin.read()
values = data.split()
height = int(values[0])
age = int(values[1])
adult = int(values[2]) == 1
if height >= 120 and (age >= 10 or adult):
    print("BOARD")
else:
    print("WAIT")
