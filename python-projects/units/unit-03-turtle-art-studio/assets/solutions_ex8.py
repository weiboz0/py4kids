# Bring in Python's turtle drawing tools.
import turtle

n = 7
side_length = 60
angle = 360 / n
turtle.color("orange")
turtle.pensize(2)

# Move backward to a new starting spot without drawing a line.
turtle.penup()
turtle.backward(40)
turtle.pendown()

# Counter values are 0, 1, 2, 3, 4, 5, 6; angle is a float.
for side_number in range(n):
    turtle.pensize(side_number + 2)
    turtle.forward(side_length)
    turtle.right(angle)

turtle.done()
