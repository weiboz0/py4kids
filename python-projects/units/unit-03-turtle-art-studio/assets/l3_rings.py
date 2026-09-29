# Drawing tools from Python's turtle.
import turtle

# Six squares, each turned a little from the last, make a ring.
for shape_number in range(6):
    for side_number in range(4):
        turtle.forward(60)
        turtle.right(90)
    turtle.right(60)

turtle.done()
