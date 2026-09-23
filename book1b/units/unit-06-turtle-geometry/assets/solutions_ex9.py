# Bring in Python's turtle drawing tools.
import turtle

# Use the honest decimal angle for a closed seven-sided comparison shape.
n = 7
side = 53
angle = 360 / n
turtle.pencolor("magenta")

# Seven equal decimal turns complete the regular heptagon.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
