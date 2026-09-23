# Bring in Python's turtle drawing tools.
import turtle

# Set up the triangular trail-sign border.
n = 3
side = 74
angle = 360 / n
turtle.pencolor("forestgreen")

# The turtle uses the 120-degree outside angle at each corner.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
