import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
times = []
i = 0
while i < n:
    times.append(int(parts[i + 1]))
    i = i + 1
times.sort()
finish_time = 0
total_completion_time = 0
i = 0
while i < n:
    finish_time = finish_time + times[i]
    total_completion_time = total_completion_time + finish_time
    i = i + 1
print(str(total_completion_time))
