OPCODES = ["LOAD", "STORE", "ADD", "SUB", "MULT", "DIV", "BE", "BG", "BL", "BU",
           "READ", "PRINT", "DC", "END"]


def div(x, y):
    q = abs(x) // abs(y)
    if x * y < 0:
        q = -q
    return q


def value(loc, memory):
    if loc[0] == "=":
        return int(loc[1:len(loc)])
    return memory[loc]


n = int(input())
ops = []
locs = []
where = {}
memory = {}
for k in range(n):
    parts = input().split()
    first = 0
    if parts[0] not in OPCODES:
        where[parts[0]] = k
        first = 1
    op = parts[first]
    loc = ""
    if first + 1 < len(parts):
        loc = parts[first + 1]
    if op == "DC":
        memory[parts[0]] = int(loc)
    ops.append(op)
    locs.append(loc)
m = int(input())
inputs = []
for k in range(m):
    inputs.append(int(input()))

next_input = 0
acc = 0
line = 0
while ops[line] != "END":
    op = ops[line]
    loc = locs[line]
    line = line + 1
    if op == "LOAD":
        acc = value(loc, memory)
    elif op == "STORE":
        memory[loc] = acc
    elif op == "ADD":
        acc = acc + value(loc, memory)
    elif op == "SUB":
        acc = acc - value(loc, memory)
    elif op == "MULT":
        acc = acc * value(loc, memory)
    elif op == "DIV":
        acc = div(acc, value(loc, memory))
    elif op == "BE":
        if acc == 0:
            line = where[loc]
    elif op == "BG":
        if acc > 0:
            line = where[loc]
    elif op == "BL":
        if acc < 0:
            line = where[loc]
    elif op == "BU":
        line = where[loc]
    elif op == "READ":
        memory[loc] = inputs[next_input]
        next_input = next_input + 1
    elif op == "PRINT":
        print(memory[loc])
