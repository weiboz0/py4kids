# Bring in Python's turtle drawing tools.
import turtle

# Draw one closed regular polygon.
def draw_polygon(sides, length):
    angle = 360 / sides
    for corner in range(sides):
        turtle.forward(length)
        turtle.left(angle)

# Draw three hexagons and return to the mural start.
def polygon_row():
    for polygon in range(3):
        draw_polygon(6, 30)
        turtle.penup()
        turtle.forward(70)
        turtle.pendown()
    turtle.penup()
    turtle.backward(210)
    turtle.pendown()

polygon_row()
turtle.done()
