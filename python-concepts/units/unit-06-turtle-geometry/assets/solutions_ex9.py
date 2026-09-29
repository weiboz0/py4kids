# Bring in Python's turtle drawing tools.
import turtle

# turtle-check: open-path
segments = 24
step = 10
dashes = 0

for i in range(segments):
    if i % 2 == 0:
        turtle.pendown()
        turtle.forward(step)
        dashes = dashes + 1
    else:
        turtle.penup()
        turtle.forward(step)

print(f"Dashes: {dashes}")
turtle.done()
