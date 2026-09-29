from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
command_count = int(parts[0])
document = deque()
part_index = 1
command_index = 0
while command_index < command_count:
    command = parts[part_index]
    if command == "TYPE":
        document.appendleft(parts[part_index + 1])
        part_index = part_index + 2
    else:
        document.popleft()
        part_index = part_index + 1
    command_index = command_index + 1
if len(document) == 0:
    print("EMPTY")
else:
    answer = deque()
    while len(document) > 0:
        answer.appendleft(document.popleft())
    result = ""
    while len(answer) > 0:
        result = result + answer.popleft()
    print(result)
