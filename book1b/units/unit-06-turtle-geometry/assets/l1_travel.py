# Bring in Python's turtle drawing tools.
import turtle

# Travel to a new starting spot without drawing.
turtle.penup()
turtle.forward(35)
turtle.pendown()

# Draw a dark green square from the new spot.
n = 4
side = 58
angle = 360 / n
turtle.pencolor("darkgreen")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
