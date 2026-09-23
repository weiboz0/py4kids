# Bring in Python's turtle drawing tools.
import turtle

# Color and pen size change the look, not the polygon rule.
n = 5
side = 88
angle = 360 / n
turtle.color("coral")
turtle.pensize(5)

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
