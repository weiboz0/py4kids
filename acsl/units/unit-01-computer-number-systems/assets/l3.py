DIGITS = "0123456789ABCDEF"


def to_base(n, base):
    if n == 0:
        return "0"
    text = ""
    while n > 0:
        text = DIGITS[n % base] + text
        n = n // base
    return text


parts = input().split()
value = int(parts[0], int(parts[1]))
print(to_base(value, int(parts[2])))
