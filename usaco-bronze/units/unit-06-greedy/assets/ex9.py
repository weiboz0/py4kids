import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
jobs = []
i = 0
while i < n:
    deadline = int(parts[i * 2 + 1])
    prize = int(parts[i * 2 + 2])
    jobs.append((deadline, prize))
    i = i + 1

def prize_amount(job):
    return job[1]

jobs = sorted(jobs, key=prize_amount, reverse=True)
used = []
j = 0
while j < n + 1:
    used.append(False)
    j = j + 1
total_prize = 0
i = 0
while i < n:
    slot = jobs[i][0]
    prize = jobs[i][1]
    while slot > 0 and used[slot]:
        slot = slot - 1
    if slot > 0:
        used[slot] = True
        total_prize = total_prize + prize
    i = i + 1
print(str(total_prize))
