# Bring in Python's turtle drawing tools.
import turtle

# Change these two values to design a different regular polygon.
n = 7
side_length = 70

# A full turn is 360 degrees.
# The / calculation can make a decimal number, called a float.
angle = 360 / n

# Set up a blue pen.
turtle.color("blue")
turtle.speed(4)
turtle.pensize(2)

# Lift the pen, move a little, and lower the pen again.
turtle.penup()
turtle.forward(20)
turtle.pendown()

# range(n) gives the counter values 0 through n - 1.
# Each trip around the loop draws one side and turns one corner.
for side_number in range(n):
    # The counter makes each new side one step thicker.
    turtle.pensize(side_number + 1)
    turtle.forward(side_length)
    turtle.right(angle)

# Keep the drawing window open until you close it.
turtle.done()
