# Student task: replace this starter with the goldenrod 96-step five-point star from Exercise 16.
import turtle

n = 4
side = 23
angle = 360 / n
turtle.pencolor("slategray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
