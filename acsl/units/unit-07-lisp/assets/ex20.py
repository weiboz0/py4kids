def show(items):
    if len(items) == 0:
        return "NIL"
    text = "("
    for k in range(len(items)):
        if k > 0:
            text = text + " "
        text = text + items[k]
    return text + ")"


def cdr(items):
    rest = []
    for k in range(1, len(items)):
        rest.append(items[k])
    return rest


name = input().strip()
line = input()
items = line[1:len(line) - 1].split()
is_list = True
atom = ""
for k in range(len(name) - 2, 0, -1):
    if name[k] == "A":
        atom = items[0]
        is_list = False
    else:
        items = cdr(items)
if is_list:
    print(show(items))
else:
    print(atom)
