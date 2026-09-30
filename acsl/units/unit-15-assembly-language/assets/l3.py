OPCODES = ["LOAD", "STORE", "ADD", "SUB", "BG", "BU", "PRINT", "DC", "END"]


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
    elif op == "BG":
        if acc > 0:
            line = where[loc]
    elif op == "BU":
        line = where[loc]
    elif op == "PRINT":
        print(memory[loc])
