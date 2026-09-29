DIGITS = "0123456789ABCDEF"

parts = input().split()
n = int(parts[0])
base = int(parts[1])
text = ""
while n > 0:
    text = DIGITS[n % base] + text
    n = n // base
answer = "YES"
left = 0
right = len(text) - 1
while left < right:
    if text[left] != text[right]:
        answer = "NO"
    left = left + 1
    right = right - 1
print(text + " " + answer)
