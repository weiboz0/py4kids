from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
stack = deque()
i = 0
while i < len(tokens):
    token = tokens[i]
    if token == "+" or token == "-" or token == "*":
        right = stack.popleft()
        left = stack.popleft()
        if token == "+":
            value = left + right
        elif token == "-":
            value = left - right
        else:
            value = left * right
        stack.appendleft(value)
    else:
        stack.appendleft(int(token))
    i = i + 1
print(str(stack.popleft()))
