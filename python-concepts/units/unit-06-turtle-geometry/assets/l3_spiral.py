# Bring in Python's turtle drawing tools.
import turtle

# turtle-check: open-path
# Increase the side after every move so the path grows outward.
side = 8
step = 5
turtle.pencolor("brown")
turtle.pensize(2)

for side_number in range(18):
    turtle.forward(side)
    turtle.left(91)
    side = side + step

turtle.done()
