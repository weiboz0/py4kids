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


def to_bits(value, width):
    text = ""
    for i in range(width):
        text = str(value % 2) + text
        value = value // 2
    return text


parts = input().split()
target = input()
width = len(target)
last = len(parts) - 1
found = 0
for value in range(2 ** width):
    x = to_bits(value, width)
    bits = x
    i = last - 1
    while i >= 0:
        bits = apply_unary(parts[i], bits)
        i = i - 1
    if bits == target:
        print(x)
        found = found + 1
if found == 0:
    print("NONE")
