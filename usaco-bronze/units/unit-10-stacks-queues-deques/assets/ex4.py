from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
signal_count = int(parts[0])
signals = []
answers = []
i = 0
while i < signal_count:
    signals.append(int(parts[i + 1]))
    answers.append(-1)
    i = i + 1
stack = deque()
i = 0
while i < signal_count:
    while len(stack) > 0 and signals[stack[0]] < signals[i]:
        weaker_index = stack[0]
        stack.popleft()
        answers[weaker_index] = signals[i]
    stack.appendleft(i)
    i = i + 1
answer_parts = []
i = 0
while i < signal_count:
    answer_parts.append(str(answers[i]))
    i = i + 1
result = ""
j = 0
while j < len(answer_parts):
    if j > 0:
        result = result + " "
    result = result + answer_parts[j]
    j = j + 1
print(result)
