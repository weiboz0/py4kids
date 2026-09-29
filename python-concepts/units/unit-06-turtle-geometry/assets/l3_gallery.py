# Bring in Python's turtle drawing tools.
import turtle

# Build the gallery design: fifteen octagons in a complete ring.
n = 8
side = 36
angle = 360 / n
shape_count = 15
turn_between_shapes = 360 / shape_count
turtle.bgcolor("white")
turtle.pencolor("navy")
turtle.pensize(2)
turtle.speed(0)

for shape in range(shape_count):
    for corner in range(n):
        turtle.forward(side)
        turtle.left(angle)
    turtle.left(turn_between_shapes)

turtle.done()
