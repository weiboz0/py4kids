import turtle
import random

random.seed(4)
sides = random.randint(3, 8)
length = 70
angle = 360 / sides

for side_number in range(sides):
    turtle.forward(length)
    turtle.right(angle)

turtle.done()
