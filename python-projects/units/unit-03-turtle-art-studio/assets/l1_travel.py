# Drawing tools from Python's turtle.
import turtle

# Lift the pen, hop forward leaving no mark, then drop the pen.
turtle.penup()
turtle.forward(80)
turtle.pendown()

# Now draw a square from the new spot.
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)
turtle.forward(100)
turtle.right(90)

turtle.done()
