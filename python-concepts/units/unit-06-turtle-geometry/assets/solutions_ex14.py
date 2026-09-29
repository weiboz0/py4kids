# Bring in Python's turtle drawing tools before calling them.
import turtle

side = 70
for corner in range(3):
    turtle.forward(side)
    turtle.left(360 / 3)

turtle.done()
