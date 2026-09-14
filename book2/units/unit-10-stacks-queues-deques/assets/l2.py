from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
stack = deque()
for token in tokens:
    if token in "+-*" and len(token) == 1:
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
print(str(stack[0]))
