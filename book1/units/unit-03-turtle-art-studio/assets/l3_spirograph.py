# Bring in Python's turtle drawing tools.
import turtle

# Each small shape is a six-sided polygon.
n = 6
side_length = 80
angle = 360 / n

# The whole picture uses 24 shapes.
shape_count = 24
turn_between_shapes = 15

# Keep one bold color for the complete design.
turtle.color("purple")
turtle.pensize(2)
turtle.speed(0)

# The outer counter tracks which polygon is being drawn.
for shape_number in range(shape_count):
    # The inner counter tracks the sides of one polygon.
    for side_number in range(n):
        turtle.forward(side_length)
        turtle.right(angle)

    # Turn before the outer loop starts the next polygon.
    turtle.right(turn_between_shapes)

# Keep the drawing window open until you close it.
turtle.done()
