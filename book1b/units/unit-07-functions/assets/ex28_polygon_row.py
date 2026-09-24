# Student task: replace the working hexagon with the Exercise 28 row.
import turtle


# Draw one closed regular polygon.
def draw_polygon(sides, length):
    angle = 360 / sides
    for corner in range(sides):
        turtle.forward(length)
        turtle.left(angle)


turtle.pencolor("gray")
draw_polygon(6, 20)

turtle.done()
