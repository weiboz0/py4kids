S = "MISSISSIPPI RIVER"
count = 0
for ch in S:
    if ch == "S" or ch == "I":
        count = count + 1
print(count, len(S))
