DIGITS = "0123456789ABCDEF"

parts = input().split()
n = int(parts[0])
base = int(parts[1])
text = ""
total = 0
if n == 0:
    text = "0"
while n > 0:
    digit = n % base
    text = DIGITS[digit] + text
    total = total + digit
    n = n // base
print(text, total)
