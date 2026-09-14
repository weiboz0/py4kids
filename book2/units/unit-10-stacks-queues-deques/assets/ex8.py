from collections import deque
import sys

data = sys.stdin.read()
text = data.split()[0]
stack = deque()
i = 0
while i < len(text):
    character = text[i]
    if len(stack) > 0 and stack[0] == character:
        stack.popleft()
    else:
        stack.appendleft(character)
    i = i + 1
if len(stack) == 0:
    print("EMPTY")
else:
    answer = deque()
    while len(stack) > 0:
        answer.appendleft(stack.popleft())
    result = ""
    while len(answer) > 0:
        result = result + answer.popleft()
    print(result)
