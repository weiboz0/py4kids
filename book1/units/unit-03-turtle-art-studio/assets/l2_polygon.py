# Drawing tools from Python's turtle.
import turtle

# Let Python compute the turn from the number of sides.
# 360 / n is a float (a decimal). The turtle turns by it just the same.
n = 7
side_length = 70
angle = 360 / n
for side in range(n):
    turtle.forward(side_length)
    turtle.right(angle)

turtle.done()
