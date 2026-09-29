# Bring in Python's turtle drawing tools.
import turtle


def polygon_points(n):
    """Return the turn angle for a regular polygon with n sides."""
    return 360 / n


def polygon(n, side_length):
    """Draw one closed regular polygon and finish where it began."""
    turn_angle = polygon_points(n)
    for side in range(n):
        turtle.forward(side_length)
        turtle.right(turn_angle)


turtle.color("purple")
turtle.pensize(3)

# Each function call uses the returned float as its turn angle.
polygon(3, 90)
turtle.right(120)
polygon(4, 70)
turtle.right(120)
polygon(5, 55)
turtle.right(120)

# Keep the drawing window open until you close it.
turtle.done()
