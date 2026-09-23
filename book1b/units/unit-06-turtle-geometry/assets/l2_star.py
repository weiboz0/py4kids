# Bring in Python's turtle drawing tools.
import turtle

# A five-point star turns through two full turns in all.
n = 5
side = 105
angle = 720 / n
turtle.pencolor("gold")
turtle.pensize(4)

for point in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
