# Student task: replace this starter with the turquoise ring of nine hexagons from Exercise 6.
import turtle

n = 4
side = 21
angle = 360 / n
turtle.pencolor("gray")

for corner in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
