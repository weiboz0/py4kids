# Bring in Python's turtle drawing tools.
import turtle

# A regular seven-sided polygon is a heptagon.
n = 7
side_length = 70
angle = 360 / n
turtle.color("purple")
turtle.pensize(1)

# Move to a new starting spot without drawing a line.
turtle.penup()
turtle.forward(20)
turtle.pendown()

# Draw the heptagon, making each new side a little thicker.
for side_number in range(n):
    turtle.pensize(side_number + 1)
    turtle.forward(side_length)
    turtle.right(angle)

turtle.done()
