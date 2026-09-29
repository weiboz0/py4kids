# Bring in Python's turtle drawing tools.
import turtle

# Travel to the map symbol's starting point without drawing a road.
turtle.penup()
turtle.forward(39)
turtle.pendown()

# Set up the octagonal map symbol.
n = 8
side = 44
angle = 360 / n
turtle.pencolor("crimson")

# Draw eight equal sides from the new starting point.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
