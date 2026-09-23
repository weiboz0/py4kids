# Bring in Python's turtle drawing tools.
import turtle

# turtle-check: open-path
# Set up an outward-growing radar spiral.
side = 11
step = 6
move_count = 14
turtle.pencolor("maroon")

# Each move grows by the same amount, so this path stays open.
for side_number in range(move_count):
    turtle.forward(side)
    turtle.left(92)
    side = side + step

turtle.done()
