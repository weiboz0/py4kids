# Student task: travel with the pen up, then draw the crimson 44-step octagon from Exercise 5.
import turtle

n = 4
side = 20
angle = 360 / n
turtle.pencolor("silver")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
