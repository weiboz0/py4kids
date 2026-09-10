# Bring in Python's turtle drawing tools.
import turtle

# Choose how the pen looks and how fast the turtle moves.
turtle.color("teal")
turtle.pensize(4)

# Draw side 1, then turn one square corner.
turtle.forward(100)
turtle.right(90)

# Draw side 2, then turn one square corner.
turtle.forward(100)
turtle.right(90)

# Draw side 3, then turn one square corner.
turtle.forward(100)
turtle.right(90)

# Draw side 4, then turn back toward the starting direction.
turtle.forward(100)
turtle.right(90)

# Keep the drawing window open until you close it.
turtle.done()
