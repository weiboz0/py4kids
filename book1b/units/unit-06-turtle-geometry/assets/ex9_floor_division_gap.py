# Student task: draw the magenta 34-step eleven-sided experiment and explain its 8-degree gap.
import turtle

n = 4
side = 24
angle = 360 / n
turtle.pencolor("dimgray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
