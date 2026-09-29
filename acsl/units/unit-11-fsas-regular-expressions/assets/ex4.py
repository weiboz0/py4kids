start = input()
finals = input().split()
t = int(input())
table = {}
for k in range(t):
    parts = input().split()
    table[(parts[0], parts[1])] = parts[2]
n = int(input())
for k in range(n):
    word = input()
    if word == "-":
        word = ""
    state = start
    for symbol in word:
        if (state, symbol) in table:
            state = table[(state, symbol)]
        else:
            state = "-"
    if state in finals:
        print("ACCEPT")
    else:
        print("REJECT")
