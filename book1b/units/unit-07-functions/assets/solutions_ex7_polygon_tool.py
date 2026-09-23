# Bring in Python's turtle drawing tools.
import turtle


# Draw one closed regular polygon.
def draw_polygon(n, side):
    angle = 360 / n
    turtle.pendown()
    for corner in range(n):
        turtle.forward(side)
        turtle.left(360 / n)
    assert abs(n * angle - 360) < 1e-6


turtle.pencolor("teal")
# Draw the badge maker's six-sided outline.
draw_polygon(6, 48)

turtle.done()
