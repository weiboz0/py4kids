word = input()

heap = [""]
for letter in word:
    heap.append(letter)
    i = len(heap) - 1
    while i > 1 and heap[i // 2] > heap[i]:
        heap[i // 2], heap[i] = heap[i], heap[i // 2]
        i = i // 2

start = 1
while start < len(heap):
    row = ""
    for i in range(start, min(2 * start, len(heap))):
        row = row + heap[i]
    print(row)
    start = 2 * start
