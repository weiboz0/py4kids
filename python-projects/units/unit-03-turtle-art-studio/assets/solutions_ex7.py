# Bring in Python's turtle drawing tools.
import turtle

# Set up a triangle trail.
side_count = 3
side_length = 90
angle = 360 / side_count
color_name = "green"
turtle.color(color_name)
turtle.pensize(2)

# Move to a new starting spot without drawing a line.
turtle.penup()
turtle.forward(30)
turtle.pendown()

# Draw three equal sides, making each new side a little thicker.
for side_number in range(side_count):
    turtle.pensize(side_number + 2)
    turtle.forward(side_length)
    turtle.right(angle)

turtle.done()
