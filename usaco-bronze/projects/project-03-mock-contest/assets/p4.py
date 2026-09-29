import sys

def skill_of(record):
    return record[1]

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0]); target = int(tokens[1])
records = []
i = 0
while i < n:
    pid = int(tokens[2 + 2 * i])
    skill = int(tokens[3 + 2 * i])
    records.append((pid, skill))
    i = i + 1
ordered = sorted(records, key=skill_of)
lo = 0
hi = n - 1
answer = "NO"
while lo < hi and answer == "NO":
    total = ordered[lo][1] + ordered[hi][1]
    if total == target:
        answer = "YES"
    elif total < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(answer)
