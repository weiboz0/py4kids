import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
k = int(parts[1])
records = set()
i = 0
while i < n:
    record = (parts[i * 2 + 2], int(parts[i * 2 + 3]))
    if record not in records:
        records.add(record)
    i = i + 1

def rank_key(record):
    return (-record[1], record[0])

ranked = sorted(records, key=rank_key)
answer = ranked[k - 1]
print(answer[0] + " " + str(answer[1]))
