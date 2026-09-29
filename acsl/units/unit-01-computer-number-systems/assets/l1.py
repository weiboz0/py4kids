n = int(input())
power = 1
while power * 2 <= n:
    power = power * 2
bits = ""
while power >= 1:
    if n >= power:
        bits = bits + "1"
        n = n - power
    else:
        bits = bits + "0"
    power = power // 2
print(bits)
