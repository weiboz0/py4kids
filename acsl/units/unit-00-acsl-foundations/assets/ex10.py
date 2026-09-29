n = int(input())
points = []
for i in range(n):
    parts = input().split()
    points.append((int(parts[0]), int(parts[1])))
best = points[0]
best_distance = abs(best[0]) + abs(best[1])
for point in points:
    x, y = point
    distance = abs(x) + abs(y)
    if distance > best_distance:
        best = point
        best_distance = distance
print(best[0], best[1])
