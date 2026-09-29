import sys

data = sys.stdin.read()
parts = data.split()
digit_count = int(parts[0])
gap = int(parts[1])
digits = []
i = 0
while i < digit_count:
    digits.append(int(parts[i + 2]))
    i = i + 1
digits = sorted(digits)
used = []
i = 0
while i < digit_count:
    used.append(False)
    i = i + 1

def search(path):
    if len(path) == digit_count:
        answer = ""
        i = 0
        while i < len(path):
            answer = answer + str(path[i])
            i = i + 1
        return answer

    choice_index = 0
    while choice_index < digit_count:
        choice = digits[choice_index]
        legal = len(path) == 0
        if len(path) > 0:
            if abs(path[-1] - choice) >= gap:
                legal = True
        if used[choice_index] == False and legal:
            used[choice_index] = True
            answer = search(path + [choice])
            used[choice_index] = False
            if answer != "NONE":
                return answer
        choice_index = choice_index + 1
    return "NONE"

print(search([]))
