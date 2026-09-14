import sys

data = sys.stdin.read()
parts = data.split()
runner_count = int(parts[0])
target = int(parts[1])
records = []
i = 0
while i < runner_count:
    bib = int(parts[i * 2 + 2])
    time = int(parts[i * 2 + 3])
    records.append((bib, time))
    i = i + 1

def finish_time(record):
    return record[1]

records = sorted(records, key=finish_time)
answer = ""
lo = 0
hi = runner_count - 1
while lo < hi and answer == "":
    pair_sum = records[lo][1] + records[hi][1]
    if pair_sum == target:
        first_bib = min(records[lo][0], records[hi][0])
        second_bib = max(records[lo][0], records[hi][0])
        answer = str(first_bib) + " " + str(second_bib)
    elif pair_sum < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(answer)
