# sample-input: 6 | 50
import turtle

sides = int(input("Number of sides: "))
side = int(input("Side length: "))
angle = 360 / sides
for corner in range(sides):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
