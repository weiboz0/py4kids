# Student task: replace this starter with the forestgreen 74-step triangle from Exercise 2.
import turtle

n = 4
side = 17
angle = 360 / n
turtle.pencolor("black")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
