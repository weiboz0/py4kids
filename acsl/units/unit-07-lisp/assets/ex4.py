line = input()
inside = line[1:len(line) - 1]
parts = inside.split()
name = parts[0]
numbers = []
for k in range(1, len(parts)):
    numbers.append(int(parts[k]))
if name == "ADD" or name == "+":
    result = 0
    for value in numbers:
        result = result + value
    print(result)
elif name == "MULT" or name == "*":
    result = 1
    for value in numbers:
        result = result * value
    print(result)
elif name == "SUB" or name == "-":
    print(numbers[0] - numbers[1])
elif name == "DIV" or name == "/":
    quotient = numbers[0] / numbers[1]
    if quotient == int(quotient):
        print(int(quotient))
    else:
        print(quotient)
elif name == "SQUARE":
    print(numbers[0] * numbers[0])
elif name == "EXP":
    result = 1
    for k in range(numbers[1]):
        result = result * numbers[0]
    print(result)
