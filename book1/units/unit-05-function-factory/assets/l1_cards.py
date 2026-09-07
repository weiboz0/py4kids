# Bring in Python's turtle drawing tools.
import turtle


def stamp(size):
    """Draw one closed square stamp and finish where it began."""
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


# Set up the pen for a greeting-card design made from strokes.
turtle.color("teal")
turtle.pensize(3)
turtle.speed(4)

# Draw a closed card border. No text command is needed.
for edge in range(2):
    turtle.forward(220)
    turtle.right(90)
    turtle.forward(140)
    turtle.right(90)

# Move from the card's top-left corner to a starting spot inside the card.
turtle.penup()
turtle.right(90)
turtle.forward(25)
turtle.left(90)
turtle.pendown()

# Make four pen-stroke stamps inside the card.
# The loop counter changes every stamp's size and horizontal starting position.
sides = 4
for side in range(sides):
    size = 18 + side * 4
    position = side * 45

    turtle.penup()
    turtle.forward(position)
    turtle.pendown()
    stamp(size)
    turtle.penup()
    turtle.backward(position)
    turtle.pendown()

# Return from the inside starting spot to the card's top-left corner.
turtle.penup()
turtle.left(90)
turtle.forward(25)
turtle.right(90)
turtle.pendown()

# Keep the drawing window open until you close it.
turtle.done()
