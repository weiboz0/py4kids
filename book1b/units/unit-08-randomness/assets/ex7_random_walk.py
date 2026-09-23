# Student task: replace this closed placeholder with the random walk from Exercise 7.
import turtle
import random

random.seed(4)

n = 4
side = 16
angle = 360 / n
turtle.pencolor("gray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
