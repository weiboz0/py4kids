# Bring in Python's turtle drawing tools.
import turtle


def stamp(size):
    """Draw one closed square stamp and finish where it began."""
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


def stamp_gallery(rings, stamps_per_ring):
    """Draw nested rings of stamps and restore the starting state."""
    for ring_number in range(rings):
        radius = 45 + ring_number * 25
        size = 18 + ring_number * 5

        for stamp_number in range(stamps_per_ring):
            turtle.penup()
            turtle.forward(radius)
            turtle.pendown()
            stamp(size)
            turtle.penup()
            turtle.backward(radius)
            turtle.pendown()
            turtle.right(360 / stamps_per_ring)

        turtle.right(360 / rings)


turtle.color("darkgreen")
turtle.pensize(2)
turtle.speed(0)

# This first self-contained call marks the drawing's start position.
stamp(24)

# The gallery function contains an outer loop and an inner loop.
# Every stamp call returns to its own starting position and direction.
stamp_gallery(3, 6)

# Keep the drawing window open until you close it.
turtle.done()
