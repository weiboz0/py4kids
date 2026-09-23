# Student task: replace this starter with the brown 14-move growing spiral from Exercise 7.
import turtle

n = 4
side = 22
angle = 360 / n
turtle.pencolor("black")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
