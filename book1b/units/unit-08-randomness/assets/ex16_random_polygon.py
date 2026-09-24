# Student task: replace this closed placeholder with the random polygon from Exercise 16.
import turtle
import random

random.seed(4)

sides = 4
length = 20
angle = 360 / sides

for side_number in range(sides):
    turtle.forward(length)
    turtle.right(angle)

turtle.done()
