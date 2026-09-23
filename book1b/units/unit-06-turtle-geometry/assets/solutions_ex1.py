# Bring in Python's turtle drawing tools.
import turtle

# Set up the four-sided courtyard outline.
n = 4
side = 62
angle = 360 / n
turtle.pencolor("royalblue")

# Repeat one equal move and one equal turn for every side.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
