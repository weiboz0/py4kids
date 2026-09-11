import sys

data = sys.stdin.read()
text = data.strip()

def value(expression):
    if expression[0] != "(":
        return int(expression)
    depth = 0
    split_at = -1
    index = 1
    while index < len(expression) - 1:
        character = expression[index]
        if character == "(":
            depth = depth + 1
        elif character == ")":
            depth = depth - 1
        elif depth == 0 and (character == "+" or character == "*"):
            split_at = index
        index = index + 1
    left = value(expression[1:split_at])
    right = value(expression[split_at + 1:len(expression) - 1])
    if expression[split_at] == "+":
        return left + right
    return left * right

print(str(value(text)))
