import sys

data = sys.stdin.read()
parts = data.split()
width = int(parts[0])
state = int(parts[1])
command_count = int(parts[2])
full_mask = (1 << width) - 1
part_index = 3
command_index = 0
result = ""
while command_index < command_count:
    command = parts[part_index]
    if command == "NOT":
        state = ~state & full_mask
        reported = state
        part_index = part_index + 1
    else:
        bit_index = int(parts[part_index + 1])
        bit = 1 << bit_index
        if command == "TEST":
            if state & bit:
                reported = 1
            else:
                reported = 0
        elif command == "SET":
            state = state | bit
            reported = state
        elif command == "CLEAR":
            state = state & (full_mask ^ bit)
            reported = state
        else:
            state = state ^ bit
            reported = state
        part_index = part_index + 2
    if command_index > 0:
        result = result + "\n"
    result = result + str(reported)
    command_index = command_index + 1
print(result)
