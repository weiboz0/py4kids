from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
stack = deque()
i = 0
while i < len(tokens):
    token = tokens[i]
    if token == "NOT":
        value = stack.popleft()
        stack.appendleft(1 - value)
    elif token == "AND" or token == "OR" or token == "IMP":
        right = stack.popleft()
        left = stack.popleft()
        if token == "AND":
            if left == 1 and right == 1:
                value = 1
            else:
                value = 0
        elif token == "OR":
            if left == 1 or right == 1:
                value = 1
            else:
                value = 0
        else:
            if left == 1 and right == 0:
                value = 0
            else:
                value = 1
        stack.appendleft(value)
    else:
        stack.appendleft(int(token))
    i = i + 1
print(str(stack.popleft()))
