from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
card_count = int(parts[0])
cards = deque()
i = 0
while i < card_count:
    cards.append(int(parts[i + 1]))
    i = i + 1
reversed_cards = deque()
while len(cards) > 0:
    reversed_cards.appendleft(cards.popleft())
answer_parts = []
while len(reversed_cards) > 0:
    answer_parts.append(str(reversed_cards.popleft()))
result = ""
j = 0
while j < len(answer_parts):
    if j > 0:
        result = result + " "
    result = result + answer_parts[j]
    j = j + 1
print(result)
