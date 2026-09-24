import turtle
import random

random.seed(4)
side = 30
for square_number in range(4):
    code = random.choice("rgb")
    if code == "r":
        turtle.pencolor("red")
    elif code == "g":
        turtle.pencolor("green")
    else:
        turtle.pencolor("blue")
    for corner in range(4):
        turtle.forward(side)
        turtle.right(90)
    turtle.penup()
    turtle.forward(side)
    turtle.pendown()

turtle.penup()
turtle.backward(120)
turtle.done()
