door = {("S", "k"): "K", ("K", "k"): "K", ("K", "t"): "T", ("T", "k"): "K"}
code = input()
state = "S"
for button in code:
    if (state, button) in door:
        state = door[(state, button)]
    else:
        state = "STUCK"
if state == "T":
    print("OPEN")
else:
    print("LOCKED")
