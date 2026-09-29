DIGITS = "0123456789ABCDEF"
parts = input().split()
code = "#"
for part in parts:
    amount = int(part)
    code = code + DIGITS[amount // 16] + DIGITS[amount % 16]
print(code)
