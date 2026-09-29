def zeros(k):
    text = ""
    for i in range(k):
        text = text + "0"
    return text


def lshift(bits, k):
    if k > len(bits):
        k = len(bits)
    return bits[k:] + zeros(k)


def rshift(bits, k):
    if k > len(bits):
        k = len(bits)
    return zeros(k) + bits[:len(bits) - k]


def lcirc(bits, k):
    k = k % len(bits)
    return bits[k:] + bits[:k]


def rcirc(bits, k):
    k = k % len(bits)
    return bits[len(bits) - k:] + bits[:len(bits) - k]


parts = input().split()
bits = parts[0]
k = int(parts[1])
print("LSHIFT-" + str(k) + " " + lshift(bits, k))
print("RSHIFT-" + str(k) + " " + rshift(bits, k))
print("LCIRC-" + str(k) + " " + lcirc(bits, k))
print("RCIRC-" + str(k) + " " + rcirc(bits, k))
