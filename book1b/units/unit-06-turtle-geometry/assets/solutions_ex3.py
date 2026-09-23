# Bring in Python's turtle drawing tools.
import turtle

# Set up an orchid pentagon with a thicker outline.
n = 5
side = 68
angle = 360 / n
turtle.pencolor("orchid")
turtle.pensize(4)

# Draw the five equal sides of the pentagon.
for side_number in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
