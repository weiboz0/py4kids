# Two closed squares share a starting point and restore the heading.
import turtle

side = 60
for corner in range(4):
    turtle.forward(side)
    turtle.left(90)

turtle.left(90)
for corner in range(4):
    turtle.forward(side)
    turtle.left(90)
turtle.right(90)

turtle.done()
