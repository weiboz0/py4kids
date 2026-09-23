# Student task: replace this starter with the orchid 68-step pentagon from Exercise 3.
import turtle

n = 4
side = 18
angle = 360 / n
turtle.pencolor("slategray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
