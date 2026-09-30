# Quick Reference

Use this as a reminder after you have met an idea in its unit.
The indented lines belong to the line above them.
Every contest program reads its whole input, works out the answer, and prints exactly that answer.

## Reading the input · Unit 1

```python
import sys
data = sys.stdin.read()    # all of standard input
tokens = data.split()      # split on spaces and newlines
n = int(tokens[0])         # a token is text: convert it
values = []
for position in range(n):  # N first, then N values
    values.append(int(tokens[position + 1]))
```

A grid of `R` rows and `C` columns, read with a moving `position`:

```python
rows = int(tokens[0])
columns = int(tokens[1])
position = 2
grid = []
for r in range(rows):
    row = []
    for c in range(columns):
        row.append(int(tokens[position]))
        position = position + 1
    grid.append(row)
corner = grid[rows - 1][columns - 1]  # grid[r][c]
```

Print values with one space between them, and nothing else:

```python
output = ""
for position in range(len(values)):
    if position > 0:
        output = output + " "
    output = output + str(values[position])
print(output)
```

Run a program with an input file: `python my_solution.py < case.txt`.

## Boolean logic · Unit 2

```python
allowed = (member or guest) and not banned
# not runs first, then and, then or
# De Morgan: not (a and b) is (not a) or (not b)
#            not (a or b) is (not a) and (not b)
majority = yes_count * 2 > n  # strict majority, no fractions
answer = tokens[1].lower()    # compare without caring about case
```

`False and …` and `True or …` never run their right side.
Trace a program on paper before you run it: predict each line, then check.

## Fast enough? · Unit 3

| Plan | Growth | Steps when N is 100,000 |
|---|---|---|
| Halve the range each step | `O(log n)` | about 17 |
| One loop | `O(n)` | 100,000 |
| Sort, then one loop | `O(n log n)` | about 1,700,000 |
| A loop inside a loop | `O(n²)` | 10,000,000,000 |

Read the constraints first, and compare the estimate with a budget of about 100,000,000 steps.
A dictionary of values already seen turns a pair search into one loop:

```python
seen = {}
for number in numbers:
    if target - number in seen:
        found = True
    seen[number] = True
```

## Sets · Unit 4

```python
roster = {"Ava", "Bo", "Cy"}  # a set literal
distinct = set()              # an empty set
distinct.add("Dia")           # adding a repeat changes nothing
distinct.discard("Bo")        # remove it if it is there
if "Ava" in roster:           # fast membership test
    print("on the roster")
only_first = first - second   # in first but not in second
print(len(distinct))          # how many distinct values
```

Build a union or an intersection with a loop:

```python
both = set()
for name in first:
    if name in second:
        both.add(name)
```

## Tuples and sorting with a key · Unit 4

```python
records = [("Ava", 18), ("Bo", 9), ("Cy", 24)]
for name, score in records:  # unpack each tuple
    print(name, score)

def by_score(record):
    return record[1]

def leaderboard_key(record):
    name, score = record
    return (-score, name)     # highest score first, then name

lowest_first = sorted(records, key=by_score)
ranked = sorted(records, key=leaderboard_key)
```

Return a negated field, such as `-score`, to put the largest first.

## Searching · Unit 5

```python
ordered = sorted(values)  # binary search needs a sorted list
found = False
lo = 0
hi = len(ordered) - 1
while lo <= hi and found == False:
    mid = (lo + hi) // 2
    if ordered[mid] == target:
        found = True
    elif ordered[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
```

Complete search tries every pair once:

```python
count = 0
for first in range(n):
    for second in range(first + 1, n):
        if values[first] + values[second] == target:
            count = count + 1
```

Search over the answer: find the smallest capacity that works, when a bigger capacity never needs more days.

```python
lo = max(weights)
hi = sum(weights)
while lo < hi:
    mid = (lo + hi) // 2
    if feasible(mid):  # your own check for one capacity
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Greedy · Unit 6

```python
def end_time(event):
    return event[1]

attended = 0
last_end = -1
for event in sorted(events, key=end_time):
    if event[0] >= last_end:  # touching events do not overlap
        attended = attended + 1
        last_end = event[1]

coins.sort(reverse=True)      # largest coin first
costs.sort()                  # cheapest first
```

Before you trust a greedy rule, try small counterexamples and tell the exchange story.

## Simulation · Unit 7

```python
charge = charge + change
if charge > capacity:  # clamp to [0, capacity]
    charge = capacity
elif charge < 0:
    charge = 0

inside = 0 <= next_row and next_row < rows
inside = inside and 0 <= next_column and next_column < columns
if inside and grid[next_row][next_column] != -1:
    robot_row = next_row
    robot_column = next_column

seen = []
while state not in seen:  # stop at the first repeat
    seen.append(state)
    state = (state * 2) % 7
```

Name the state, apply the rules in the given order, guard every edge, and make sure the loop stops.

## Prefix sums · Unit 8

```python
pre = [0]
for i in range(len(a)):
    pre.append(pre[i] + a[i])
total = pre[right + 1] - pre[left]  # a[left] through a[right]
```

A prefix grid has one extra zero row and one extra zero column:

```python
above = pre[r][c + 1]
left = pre[r + 1][c]
overlap = pre[r][c]
pre[r + 1][c + 1] = grid[r][c] + above + left - overlap

total = pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1]
total = total - pre[r2 + 1][c1] + pre[r1][c1]
```

## Recursion and backtracking · Unit 9

```python
def factorial(value):
    if value == 0:  # the base case stops the calls
        return 1
    return value * factorial(value - 1)

def search(index, total):  # count subsets that hit target
    if index == n:
        if total == target:
            return 1
        return 0
    with_value = search(index + 1, total + values[index])
    without_value = search(index + 1, total)
    return with_value + without_value
```

Mark a choice, recurse, then undo it before the next choice:

```python
used[choice_index] = True
ways = ways + search(path + [choice])
used[choice_index] = False
```

## Stacks and queues · Unit 10

```python
from collections import deque
stack = deque()
stack.appendleft(item)   # push
top = stack[0]           # peek at the newest
stack.popleft()          # pop the newest

queue = deque()
queue.append(item)       # join at the back
first = queue.popleft()  # serve the oldest
empty = len(queue) == 0  # check before you peek or pop
```

In postfix, pop the right value first, then the left: `right = stack.popleft()`, then `left = stack.popleft()`.

## Number systems and bits · Unit 11

```python
digits = "0123456789ABCDEF"
text = ""
while number > 0:             # decimal to another base
    text = digits[number % base] + text
    number = number // base   # (the number 0 is "0")

value = 0
for bit in binary_text:        # binary back to decimal
    value = value * 2 + int(bit)
```

```python
mask = 1 << k                  # only bit k is on
full_mask = (1 << width) - 1   # the lowest width bits on
if state & mask:               # is bit k on?
    print("on")
state = state | mask           # set bit k
state = state & (full_mask ^ mask)  # clear bit k
state = state ^ mask           # flip bit k
flipped = ~state & full_mask   # flip every bit in the width

for subset in range(1 << n):   # every subset of n items
    total = 0
    for i in range(n):
        if subset & (1 << i):  # item i is in the subset
            total = total + values[i]
```

```python
x = a
y = b
while y != 0:                  # Euclid's algorithm
    x, y = y, x % y
gcd = x
lcm = a // gcd * b             # divide first, then multiply

answer = answer * current % m  # reduce after every multiply
```

A sieve finds every prime up to N: for each prime `p`, mark `p*p`, `p*p + p`, … as not prime.

## Binary trees · Unit 12

```python
order = []
def preorder(node):
    if node == -1:              # -1 means no child
        return
    order.append(val[node])     # visit the node first
    preorder(left[node])
    preorder(right[node])
```

For in-order, visit the node between the two subtrees; for post-order, visit it after both.
In a binary search tree, compare the target with the node and go one way only:

```python
node = root
while node != -1 and val[node] != target:
    if target < val[node]:
        node = left[node]
    else:
        node = right[node]
```

## Grids and graphs · Unit 13

```python
dr = [-1, 1, 0, 0]              # up, down, left, right
dc = [0, 0, -1, 1]
for direction in range(4):
    nr = r + dr[direction]
    nc = c + dc[direction]
    if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
        print(grid[nr][nc])

adj = {}
for u, v in edges:              # an undirected edge
    if u not in adj:
        adj[u] = []
    if v not in adj:
        adj[v] = []
    adj[u].append(v)
    adj[v].append(u)
```

Breadth-first search finds the fewest steps:

```python
from collections import deque
queue = deque()
queue.append(start)
distance = {start: 0}
while len(queue) > 0:
    current = queue.popleft()   # the oldest first
    for nxt in adj[current]:
        if nxt not in distance:
            distance[nxt] = distance[current] + 1
            queue.append(nxt)
```

Depth-first search and flood fill mark what they visit:

```python
def dfs(node, visited):
    visited.add(node)
    for neighbour in adj[node]:
        if neighbour not in visited:
            dfs(neighbour, visited)
```

## Two pointers · Unit 14

```python
lo = 0                          # the list must be sorted
hi = len(values) - 1
found = False
while lo < hi and found == False:
    total = values[lo] + values[hi]
    if total == target:
        found = True
    elif total < target:
        lo = lo + 1             # need a bigger sum
    else:
        hi = hi - 1             # need a smaller sum
```

A sliding window keeps a running sum; its values must not be negative:

```python
left = 0
window_sum = 0
best = 0
for right in range(len(values)):
    window_sum = window_sum + values[right]
    while window_sum > limit and left <= right:
        window_sum = window_sum - values[left]
        left = left + 1
    best = max(best, right - left + 1)
```
