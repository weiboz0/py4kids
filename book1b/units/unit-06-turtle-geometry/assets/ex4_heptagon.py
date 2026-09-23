# Student task: replace this starter with the dark-orange 57-step heptagon from Exercise 4.
import turtle

n = 4
side = 19
angle = 360 / n
turtle.pencolor("dimgray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
