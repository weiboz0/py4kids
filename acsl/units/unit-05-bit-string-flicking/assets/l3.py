def to_bits(value, width):
    text = ""
    for i in range(width):
        text = str(value % 2) + text
        value = value // 2
    return text


target_text = input()
width = len(target_text)
target = int(target_text, 2)
mask = 2 ** width - 1
found = 0
for x in range(2 ** width):
    if ((x >> 1) ^ x) & mask == target:
        print(to_bits(x, width))
        found = found + 1
if found == 0:
    print("NONE")
