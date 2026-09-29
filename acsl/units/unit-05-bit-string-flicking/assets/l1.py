def pad_left(bits, width):
    while len(bits) < width:
        bits = "0" + bits
    return bits


def combine(a, op, b):
    width = max(len(a), len(b))
    a = pad_left(a, width)
    b = pad_left(b, width)
    result = ""
    for i in range(width):
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
print(combine(parts[0], parts[1], parts[2]))
