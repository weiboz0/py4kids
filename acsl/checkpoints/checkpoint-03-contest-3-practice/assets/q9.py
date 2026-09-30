parts = input().split()
n = int(parts[0])
k = int(parts[1])
queue = []
for player in range(1, n + 1):
    queue.append(player)
head = 0
order = ""
while head < len(queue):
    for step in range(k - 1):
        queue.append(queue[head])
        head = head + 1
    player = queue[head]
    head = head + 1
    if order == "":
        order = str(player)
    else:
        order = order + " " + str(player)
print(order)
