# Bring in Python's turtle drawing tools.
import turtle

# Each small shape is a six-sided polygon.
n = 6
side_length = 80
angle = 360 / n
turn_between_shapes = 15

# Set up the pen for a rainbow ring of 24 shapes.
turtle.pensize(2)

# Draw four red polygons.
turtle.color("red")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Draw four orange polygons.
turtle.color("orange")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Draw four yellow polygons.
turtle.color("yellow")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Draw four green polygons.
turtle.color("green")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Draw four blue polygons.
turtle.color("blue")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Draw four purple polygons.
turtle.color("purple")
for shape_number in range(4):
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.right(turn_between_shapes)

# Keep the finished drawing open until you close it.
turtle.done()
