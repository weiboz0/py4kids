import sys

data = sys.stdin.read()
tokens = data.split()
kid_count = int(tokens[0])
snack_count = int(tokens[1])
needs = []
i = 0
while i < kid_count:
    needs.append(int(tokens[2 + i]))
    i = i + 1
snacks = []
i = 0
while i < snack_count:
    snacks.append(int(tokens[2 + kid_count + i]))
    i = i + 1
needs.sort()
snacks.sort()

happy = 0
kid = 0
snack = 0
while kid < kid_count and snack < snack_count:
    if snacks[snack] >= needs[kid]:
        happy = happy + 1
        kid = kid + 1
    snack = snack + 1
print(str(happy))
