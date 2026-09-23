# Bring in Python's turtle drawing tools.
import turtle

# Set up the seven-sided game token.
n = 7
side = 57
angle = 360 / n
turtle.pencolor("darkorange")

# angle is a float, and all seven turns total 360 degrees.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
