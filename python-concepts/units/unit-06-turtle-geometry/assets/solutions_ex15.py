# Bring in Python's turtle drawing tools.
import turtle

side = 60
n = 5

# Both drawing commands belong inside the loop body.
for corner in range(n):
    turtle.forward(side)
    turtle.left(360 / n)

turtle.done()
