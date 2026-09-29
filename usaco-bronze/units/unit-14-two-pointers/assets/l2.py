import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
limit = int(tokens[1])
values = []
i = 0
while i < n:
    values.append(int(tokens[i + 2]))
    i = i + 1

left = 0
right = 0
window_sum = 0
best_length = 0
while right < n:
    window_sum = window_sum + values[right]
    while window_sum > limit and left <= right:
        window_sum = window_sum - values[left]
        left = left + 1
    current_length = right - left + 1
    if current_length > best_length:
        best_length = current_length
    right = right + 1
print(str(best_length))
