import sys

data = sys.stdin.read()
parts = data.split()
registered = parts[0] == "1"
guest = parts[1] == "1"
badge = parts[2] == "1"
blocked = parts[3] == "1"
coach = parts[4] == "1"
is_open = not blocked and (registered or guest) and (badge or coach)
if is_open:
    print("OPEN")
else:
    print("CLOSED")
