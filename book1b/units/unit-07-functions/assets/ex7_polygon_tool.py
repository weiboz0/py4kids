# Student task: use this working square example to draw the teal hexagon from Exercise 7.
import turtle


# Draw one closed regular polygon.
def draw_polygon(n, side):
    angle = 360 / n
    turtle.pendown()
    for corner in range(n):
        turtle.forward(side)
        turtle.left(angle)


turtle.pencolor("gray")
draw_polygon(4, 24)

turtle.done()
