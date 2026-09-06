# Bring in Python's turtle drawing tools.
import turtle

# This solution chooses a regular five-sided polygon.
n = 5
side_length = 90
angle = 360 / n

# Set up the pen.
turtle.color("blue")
turtle.pensize(3)
turtle.speed(4)

# Each loop trip draws one side of the pentagon.
for side_number in range(n):
    turtle.forward(side_length)
    turtle.right(angle)

# Keep the finished drawing open until you close it.
turtle.done()
