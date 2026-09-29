DIGITS = "0123456789ABCDEF"


def to_base(n, base):
    if n == 0:
        return "0"
    text = ""
    while n > 0:
        text = DIGITS[n % base] + text
        n = n // base
    return text


def is_palindrome(text):
    last = len(text) - 1
    for i in range(len(text)):
        if text[i] != text[last - i]:
            return False
    return True


parts = input().split()
a = int(parts[0])
b = int(parts[1])
total = 0
for number in range(a, b + 1):
    if is_palindrome(str(number)):
        if is_palindrome(to_base(number, 2)):
            total = total + 1
print(total)
