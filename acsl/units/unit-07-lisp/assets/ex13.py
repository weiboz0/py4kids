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


def reverse(items):
    result = []
    for k in range(len(items) - 1, -1, -1):
        result.append(items[k])
    return result


line = input()
atoms = line[1:len(line) - 1].split()
print(show(reverse(atoms)))
print(show(reverse(cdr(atoms))))
