# Bring in Python's turtle drawing tools.
import turtle

# Use the honest decimal angle for a closed eleven-sided comparison shape.
n = 11
side = 34
angle = 360 / n
turtle.pencolor("magenta")

# Eleven equal decimal turns complete the regular hendecagon.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
