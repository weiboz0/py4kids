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


parts = input().split()
or_value = ""
xor_value = ""
and_value = ""
start = 0
for i in range(len(parts)):
    token = parts[i]
    if token == "AND":
        start = i + 1
    elif token == "XOR" or token == "OR":
        if xor_value == "":
            xor_value = and_value
        else:
            xor_value = combine(xor_value, "XOR", and_value)
        and_value = ""
        if token == "OR":
            if or_value == "":
                or_value = xor_value
            else:
                or_value = combine(or_value, "OR", xor_value)
            xor_value = ""
        start = i + 1
    elif token[0] == "0" or token[0] == "1":
        bits = token
        j = i - 1
        while j >= start:
            bits = apply_unary(parts[j], bits)
            j = j - 1
        if and_value == "":
            and_value = bits
        else:
            and_value = combine(and_value, "AND", bits)
if xor_value == "":
    xor_value = and_value
else:
    xor_value = combine(xor_value, "XOR", and_value)
if or_value == "":
    or_value = xor_value
else:
    or_value = combine(or_value, "OR", xor_value)
print(or_value)
