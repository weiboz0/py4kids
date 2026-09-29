import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
rows = int(header[0]); cols = int(header[1])
start = lines[1].split()
r = int(start[0]); c = int(start[1])
moves = ""
if len(lines) > 2:
    moves = lines[2]
i = 0
while i < len(moves):
    m = moves[i]
    nr = r; nc = c
    if m == "U":
        nr = r - 1
    if m == "D":
        nr = r + 1
    if m == "L":
        nc = c - 1
    if m == "R":
        nc = c + 1
    if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
        r = nr; c = nc
    i = i + 1
print(str(r) + " " + str(c))
