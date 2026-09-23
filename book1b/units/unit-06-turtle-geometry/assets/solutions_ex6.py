# Bring in Python's turtle drawing tools.
import turtle

# Set up one hexagon and the nine-shape wheel.
n = 6
side = 41
angle = 360 / n
shape_count = 9
turn_between_shapes = 360 / shape_count
turtle.pencolor("turquoise")

# The outer loop repeats whole hexagons around the wheel.
for shape in range(shape_count):
    # The inner loop finishes all six sides of one hexagon.
    for corner in range(n):
        turtle.forward(side)
        turtle.left(angle)
    turtle.left(turn_between_shapes)

turtle.done()
