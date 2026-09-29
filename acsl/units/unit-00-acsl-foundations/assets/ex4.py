n = int(input())
parts = input().split()
scores = []
for i in range(n):
    scores.append(int(parts[i]))
print(max(scores) - min(scores))
