import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
jobs = []
i = 0
while i < n:
    duration = int(parts[i * 2 + 1])
    deadline = int(parts[i * 2 + 2])
    jobs.append((duration, deadline))
    i = i + 1

def job_deadline(job):
    return job[1]

jobs = sorted(jobs, key=job_deadline)
finish_time = 0
worst_lateness = 0
i = 0
while i < n:
    duration = jobs[i][0]
    deadline = jobs[i][1]
    finish_time = finish_time + duration
    lateness = finish_time - deadline
    if lateness > worst_lateness:
        worst_lateness = lateness
    i = i + 1
print(str(worst_lateness))
