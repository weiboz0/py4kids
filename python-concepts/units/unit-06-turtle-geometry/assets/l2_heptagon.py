# Bring in Python's turtle drawing tools.
import turtle

# Seven equal decimal turns close a regular heptagon.
n = 7
side = 64
angle = 360 / n
turtle.pencolor("purple")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
