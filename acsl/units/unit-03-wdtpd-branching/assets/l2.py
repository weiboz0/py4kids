parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = int(parts[2])
if a + b <= c or a + c <= b or b + c <= a:
    print("NOT A TRIANGLE")
elif a == b and b == c:
    print("EQUILATERAL")
elif a == b or b == c or a == c:
    print("ISOSCELES")
else:
    if a * a + b * b == c * c or a * a + c * c == b * b or b * b + c * c == a * a:
        print("RIGHT SCALENE")
    else:
        print("SCALENE")
