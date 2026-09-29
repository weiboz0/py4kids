def show(items):
    if len(items) == 0:
        return "NIL"
    text = "("
    for k in range(len(items)):
        if k > 0:
            text = text + " "
        text = text + items[k]
    return text + ")"


line = input()
inside = line[1:len(line) - 1]
items = inside.split()
rest = []
for k in range(1, len(items)):
    rest.append(items[k])
print(items[0])
print(show(rest))
