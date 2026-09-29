n = int(input())
names = ""
for i in range(n):
    parts = input().split()
    name = parts[0]
    score = int(parts[1])
    if score >= 80:
        if names == "":
            names = name
        else:
            names = names + " " + name
if names == "":
    print("NONE")
else:
    print(names)
