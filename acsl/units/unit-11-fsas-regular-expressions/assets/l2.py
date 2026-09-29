door = {("S", "k"): "K", ("K", "k"): "K", ("K", "t"): "T", ("T", "k"): "K"}


def opens(code):
    state = "S"
    for button in code:
        if (state, button) in door:
            state = door[(state, button)]
        else:
            state = "STUCK"
    return state == "T"


def count(code, n):
    if len(code) == n:
        if opens(code):
            return 1
        return 0
    return count(code + "k", n) + count(code + "t", n)


n = int(input())
print(count("", n))
