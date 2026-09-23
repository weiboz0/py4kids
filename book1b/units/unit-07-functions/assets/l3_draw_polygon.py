# Bring in Python's turtle drawing tools.
import turtle


# Draw one closed regular polygon.
def draw_polygon(n, side):
    angle = 360 / n
    turtle.pendown()
    for corner in range(n):
        turtle.forward(side)
        turtle.left(angle)


turtle.pencolor("darkviolet")
draw_polygon(6, 56)

turtle.done()
