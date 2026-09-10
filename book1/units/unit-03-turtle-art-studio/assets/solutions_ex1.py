# Bring in Python's turtle drawing tools.
import turtle

# Set up the square studio.
straight_sides = 4
side_length = 80
angle = 360 / straight_sides
turtle.color("teal")
turtle.pensize(1)

# Draw four equal sides, making each new side a little thicker.
for side_number in range(straight_sides):
    turtle.pensize(side_number + 1)
    turtle.forward(side_length)
    turtle.right(angle)

turtle.done()
