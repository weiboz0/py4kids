# Bring in Python's turtle drawing tools.
import turtle

# Set up a five-point stage logo.
n = 5
side = 96
angle = 720 / n
turtle.pencolor("goldenrod")
turtle.pensize(3)

# A star crosses its center, so its turns make two full 360-degree turns.
for point in range(n):
    turtle.forward(side)
    turtle.left(angle)

turtle.done()
