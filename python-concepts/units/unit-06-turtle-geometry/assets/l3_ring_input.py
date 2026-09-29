# sample-input: 8
import turtle

shapes = int(input("Number of shapes: "))
side = 36
turn_between_shapes = 360 / shapes
for shape in range(shapes):
    for corner in range(4):
        turtle.forward(side)
        turtle.left(90)
    turtle.left(turn_between_shapes)

turtle.done()
