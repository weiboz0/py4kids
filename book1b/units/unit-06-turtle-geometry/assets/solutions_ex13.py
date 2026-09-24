# Bring in Python's turtle drawing tools.
import turtle

# The command is forward, with the r after the first o.
side = 50
for corner in range(4):
    turtle.forward(side)
    turtle.left(90)

turtle.done()
