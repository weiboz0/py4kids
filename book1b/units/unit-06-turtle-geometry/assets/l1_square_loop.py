# Bring in Python's turtle drawing tools.
import turtle

# A loop repeats one side and one turn four times.
n = 4
side = 73
angle = 360 / n
turtle.pencolor("teal")

for side_number in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
