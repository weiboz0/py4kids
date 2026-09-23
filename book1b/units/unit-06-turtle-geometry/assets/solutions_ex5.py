# Bring in Python's turtle drawing tools.
import turtle

# Travel to the map symbol's starting point without drawing a road.
turtle.penup()
turtle.forward(39)
turtle.pendown()

# Set up the square map symbol.
n = 4
side = 46
angle = 360 / n
turtle.pencolor("crimson")

# Draw four equal sides from the new starting point.
for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
