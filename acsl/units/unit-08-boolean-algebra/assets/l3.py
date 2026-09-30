want = int(input())
answer = ""
found = 0
for a in range(2):
    for b in range(2):
        for c in range(2):
            value = int(((a and b) != c) or (not a and not c))
            if value == want:
                if found > 0:
                    answer = answer + ", "
                answer = answer + "(" + str(a) + "," + str(b) + "," + str(c) + ")"
                found = found + 1
print(found)
if found == 0:
    print("NONE")
else:
    print(answer)
