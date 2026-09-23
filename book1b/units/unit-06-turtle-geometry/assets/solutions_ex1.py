# Bring in Python's turtle drawing tools.
import turtle

# Set up the four-sided courtyard outline.
n = 4
side = 62
angle = 360 / n
turtle.pencolor("royalblue")

# Each trip traces one courtyard edge and aims the turtle toward the next corner.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
