line = input()
inside = line[1:len(line) - 1]
parts = inside.split()
name = parts[0]
numbers = []
for k in range(1, len(parts)):
    numbers.append(int(parts[k]))
result = 0
if name == "ADD":
    for value in numbers:
        result = result + value
elif name == "MULT":
    result = 1
    for value in numbers:
        result = result * value
elif name == "SUB":
    result = numbers[0] - numbers[1]
print(result)
