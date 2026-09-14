import sys

data = sys.stdin.read()
parts = data.split()
signal_count = int(parts[0])
lone_code = 0
i = 0
while i < signal_count:
    lone_code = lone_code ^ int(parts[i + 1])
    i = i + 1
print(str(lone_code))
