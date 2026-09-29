h = int(input())
bounces = 0
distance = h
while h >= 10:
    h = h * 3 // 5
    bounces = bounces + 1
    distance = distance + 2 * h
print(bounces, distance)
