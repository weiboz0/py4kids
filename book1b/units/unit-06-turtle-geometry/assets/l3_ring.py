# Bring in Python's turtle drawing tools.
import turtle

# Draw a ring of ten hexagons with one loop inside another.
n = 6
side = 44
angle = 360 / n
shape_count = 10
turn_between_shapes = 360 / shape_count
turtle.pencolor("darkcyan")
turtle.pensize(2)

for shape in range(shape_count):
    for corner in range(n):
        turtle.forward(side)
        turtle.left(angle)
    turtle.left(turn_between_shapes)

turtle.done()
