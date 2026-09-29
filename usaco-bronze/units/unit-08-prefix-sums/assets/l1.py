import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
query_count = int(tokens[1])
values = []
value_index = 0
while value_index < n:
    values.append(int(tokens[2 + value_index]))
    value_index = value_index + 1

pre = []
pre.append(0)
value_index = 0
while value_index < n:
    pre.append(pre[value_index] + values[value_index])
    value_index = value_index + 1

answer_text = ""
token_position = 2 + n
query_index = 0
while query_index < query_count:
    left = int(tokens[token_position])
    right = int(tokens[token_position + 1])
    range_total = pre[right + 1] - pre[left]
    if query_index > 0:
        answer_text = answer_text + "\n"
    answer_text = answer_text + str(range_total)
    token_position = token_position + 2
    query_index = query_index + 1
print(answer_text)
