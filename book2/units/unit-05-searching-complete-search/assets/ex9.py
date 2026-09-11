import sys

data = sys.stdin.read()
parts = data.split()
target_sum = int(parts[0])
target_product = int(parts[1])
answer = "NONE"
first = 1
while first <= 9 and answer == "NONE":
    second = 0
    while second <= 9 and answer == "NONE":
        third = 0
        while third <= 9 and answer == "NONE":
            digit_sum = first + second + third
            digit_product = first * second * third
            if digit_sum == target_sum and digit_product == target_product:
                answer = str(first * 100 + second * 10 + third)
            third = third + 1
        second = second + 1
    first = first + 1
print(answer)
