k = int(input())
answer = ""
for i in range(k):
    parts = input().split()
    total = 0
    position = 0
    value = int(parts[position])
    while value != 0:
        total = total + value
        position = position + 1
        value = int(parts[position])
    if answer == "":
        answer = str(total)
    else:
        answer = answer + " " + str(total)
print(answer)
