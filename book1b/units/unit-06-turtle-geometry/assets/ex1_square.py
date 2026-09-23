# Student task: replace this starter with the royal-blue 62-step square from Exercise 1.
import turtle

n = 4
side = 16
angle = 360 / n
turtle.pencolor("gray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
