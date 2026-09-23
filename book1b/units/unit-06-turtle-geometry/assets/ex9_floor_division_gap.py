# Student task: draw the magenta 53-step heptagon experiment and explain its 3-degree gap.
import turtle

n = 4
side = 24
angle = 360 / n
turtle.pencolor("dimgray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
