def out_of_order(parent, child, kind):
    if kind == "MIN":
        return parent > child
    return parent < child


kind = input()
heap = [0]
for text in input().split():
    heap.append(int(text))
    i = len(heap) - 1
    while i > 1 and out_of_order(heap[i // 2], heap[i], kind):
        heap[i // 2], heap[i] = heap[i], heap[i // 2]
        i = i // 2

start = 1
while start < len(heap):
    row = str(heap[start])
    for i in range(start + 1, min(2 * start, len(heap))):
        row = row + " " + str(heap[i])
    print(row)
    start = 2 * start
