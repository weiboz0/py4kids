column = input().split()[0]
size = len(column)
n = 0
power = 1
while power < size:
    power = power * 2
    n = n + 1

answer = ""
for i in range(size):
    if column[i] == "1":
        piece = "("
        for k in range(n - 1, -1, -1):
            piece = piece + str(i // 2 ** k % 2)
            if k > 0:
                piece = piece + ","
        piece = piece + ")"
        if answer != "":
            answer = answer + ", "
        answer = answer + piece

if answer == "":
    print("NONE")
else:
    print(answer)
