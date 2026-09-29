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


parts = input().split()
last = len(parts) - 1
bits = parts[last]
i = last - 1
while i >= 0:
    bits = apply_unary(parts[i], bits)
    i = i - 1
print(bits)
