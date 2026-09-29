import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
yes_count = 0
found_no = False
for position in range(n):
    answer = tokens[position + 1].lower()
    if answer == "yes":
        yes_count = yes_count + 1
    else:
        found_no = True
if yes_count * 2 > n and found_no:
    print("YES")
else:
    print("NO")
