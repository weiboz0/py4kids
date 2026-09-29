from collections import deque
import sys

data = sys.stdin.read()
expression = data.strip()
stack = deque()
answer = "YES"
for character in expression:
    if character in "([{":
        stack.appendleft(character)
    else:
        if len(stack) == 0:
            answer = "NO"
        else:
            expected = "("
            if character == "]":
                expected = "["
            elif character == "}":
                expected = "{"
            if stack[0] != expected:
                answer = "NO"
            else:
                stack.popleft()
if len(stack) > 0:
    answer = "NO"
print(answer)
