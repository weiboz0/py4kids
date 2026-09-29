from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
command_count = int(parts[0])
line = deque()
served = []
part_index = 1
command_index = 0
while command_index < command_count:
    command = parts[part_index]
    if command == "ARRIVE":
        line.append(parts[part_index + 1])
        part_index = part_index + 2
    else:
        served.append(line.popleft())
        part_index = part_index + 1
    command_index = command_index + 1
result = ""
j = 0
while j < len(served):
    if j > 0:
        result = result + "\n"
    result = result + served[j]
    j = j + 1
print(result)
