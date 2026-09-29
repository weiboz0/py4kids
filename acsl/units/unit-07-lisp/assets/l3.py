def show(items):
    if len(items) == 0:
        return "NIL"
    text = "("
    for k in range(len(items)):
        if k > 0:
            text = text + " "
        text = text + items[k]
    return text + ")"


def car(items):
    return items[0]


def cdr(items):
    rest = []
    for k in range(1, len(items)):
        rest.append(items[k])
    return rest


def cons(first, items):
    result = [first]
    for item in items:
        result.append(item)
    return result


def swap(items):
    return cons(car(cdr(items)), cons(car(items), cdr(cdr(items))))


line = input()
bag = line[1:len(line) - 1].split()
print(show(cons(car(bag), swap(cdr(bag)))))
