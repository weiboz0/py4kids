def zeros(k):
    text = ""
    for i in range(k):
        text = text + "0"
    return text


def flip(bits):
    result = ""
    for i in range(len(bits)):
        if bits[i] == "0":
            result = result + "1"
        else:
            result = result + "0"
    return result


def apply_unary(op, bits):
    if op == "NOT":
        return flip(bits)
    pieces = op.split("-")
    name = pieces[0]
    k = int(pieces[1])
    n = len(bits)
    if name == "LSHIFT" or name == "RSHIFT":
        if k > n:
            k = n
        if name == "LSHIFT":
            return bits[k:] + zeros(k)
        return zeros(k) + bits[:n - k]
    k = k % n
    if name == "LCIRC":
        return bits[k:] + bits[:k]
    return bits[n - k:] + bits[:n - k]


def combine(a, op, b):
    result = ""
    for i in range(len(a)):
        if op == "AND":
            one = a[i] == "1" and b[i] == "1"
        elif op == "OR":
            one = a[i] == "1" or b[i] == "1"
        else:
            one = a[i] != b[i]
        if one:
            result = result + "1"
        else:
            result = result + "0"
    return result


board = input()
n = int(input())
for c in range(n):
    parts = input().split()
    op = parts[0]
    if op == "AND" or op == "OR" or op == "XOR":
        board = combine(board, op, parts[1])
    else:
        board = apply_unary(op, board)
    print(board)
