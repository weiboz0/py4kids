# Bring in Python's turtle drawing tools.
import turtle

turtle.color("blue")
turtle.pensize(1)

# The outer loop draws four whole squares.
for shape_number in range(4):
    turtle.pensize(shape_number + 1)

    # The inner loop draws the four sides of one square.
    for side_number in range(4):
        side_label = side_number + 1
        turtle.forward(60)
        turtle.right(90)

    # Travel to the starting point of the next square without drawing.
    turtle.penup()
    turtle.forward(120)
    turtle.right(90)
    turtle.pendown()

turtle.done()
