# Bring in Python's turtle drawing tools.
import turtle

# Each trip traces one square edge and aims the turtle toward the next corner.
n = 4
side = 73
angle = 360 / n
turtle.pencolor("teal")

for side_number in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
