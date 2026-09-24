# Bring in Python's turtle drawing tools.
import turtle

squares = 4
side = 40
travel = 60

# Draw each square, then travel to the next starting point without ink.
for square in range(squares):
    for corner in range(4):
        turtle.forward(side)
        turtle.left(90)
    turtle.penup()
    turtle.forward(travel)
    turtle.pendown()

# Four travels put the turtle 240 steps away; return to the start.
turtle.penup()
turtle.backward(240)
turtle.done()
