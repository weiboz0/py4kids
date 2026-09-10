# Drawing tools from Python's turtle.
import turtle

# The outer loop draws a whole square, then turns halfway around.
for shape_number in range(2):
    for side_number in range(4):
        turtle.forward(90)
        turtle.right(90)
    turtle.right(180)

turtle.done()
