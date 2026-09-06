# Bring in Python's turtle drawing tools.
import turtle

# Set up a teal pen for the four-sided answer.
turtle.color("teal")
turtle.pensize(4)
turtle.speed(3)

# Four equal moves and four 90-degree turns make a square.
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)

# The turtle is back at its start and faces its first direction.
turtle.done()
