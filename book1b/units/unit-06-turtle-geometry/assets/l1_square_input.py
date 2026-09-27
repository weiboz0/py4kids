# sample-input: 60
import turtle

side = int(input("Side length: "))
for corner in range(4):
    turtle.forward(side)
    turtle.left(90)

turtle.done()
