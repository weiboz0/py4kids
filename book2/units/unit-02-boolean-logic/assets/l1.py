import sys

data = sys.stdin.read()
values = data.split()
member = int(values[0]) == 1
guest = int(values[1]) == 1
banned = int(values[2]) == 1
if (member or guest) and not banned:
    print("GRANTED")
else:
    print("DENIED")
