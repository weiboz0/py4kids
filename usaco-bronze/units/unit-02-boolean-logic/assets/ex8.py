import sys

data = sys.stdin.read()
values = data.split()
student = int(values[0]) == 1
mentor = int(values[1]) == 1
badge = int(values[2]) == 1
banned = int(values[3]) == 1
emergency = int(values[4]) == 1
if ((not banned) and ((student or mentor) and badge)) or (emergency and mentor):
    print("OPEN")
else:
    print("CLOSED")
