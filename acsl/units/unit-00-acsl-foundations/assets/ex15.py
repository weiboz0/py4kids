n = int(input())
parts = input().split()
sticks = []
for i in range(n):
    sticks.append(int(parts[i]))
count = 0
largest = 0
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            a = sticks[i]
            b = sticks[j]
            c = sticks[k]
            if a < b + c and b < a + c and c < a + b:
                count = count + 1
                perimeter = a + b + c
                if perimeter > largest:
                    largest = perimeter
print(count, largest)
