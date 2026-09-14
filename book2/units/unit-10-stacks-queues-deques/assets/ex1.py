from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
bracket_count = int(parts[0])
brackets = ""
if bracket_count > 0:
    brackets = parts[1]
matching_open = {")": "(", "]": "[", "}": "{"}
stack = deque()
answer = "YES"
i = 0
while i < bracket_count:
    bracket = brackets[i]
    if bracket == "(" or bracket == "[" or bracket == "{":
        stack.appendleft(bracket)
    else:
        if len(stack) == 0:
            answer = "NO"
        elif stack[0] != matching_open[bracket]:
            answer = "NO"
        else:
            stack.popleft()
    i = i + 1
if len(stack) > 0:
    answer = "NO"
print(answer)
