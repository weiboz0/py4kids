n = int(input())
best_k = 1
best_sum = 0
for k in range(1, n + 1):
    s = 0
    for j in range(1, k // 2 + 1):
        if k % j == 0:
            s = s + j
    if s > best_sum:
        best_k = k
        best_sum = s
print(best_k, best_sum)
