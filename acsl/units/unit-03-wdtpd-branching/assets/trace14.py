word = input()
first = word[:3]
last = word[len(word) - 3:]
middle = word[2:6]
code = last.upper() + first.lower()
if "a" in middle:
    code = code.replace("a", "@")
print(code, middle, len(code))
