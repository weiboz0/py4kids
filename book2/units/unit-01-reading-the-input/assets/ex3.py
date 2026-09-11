import sys

data = sys.stdin.read()
parts = data.split()
k = int(parts[0])
position = 1
answer = ""
for line_number in range(k):
    count = int(parts[position])
    position = position + 1
    total = 0
    for i in range(count):
        total = total + int(parts[position])
        position = position + 1
    if line_number > 0:
        answer = answer + " "
    answer = answer + str(total)
print(answer)
