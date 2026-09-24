# Bring in Python's turtle drawing tools.
import turtle

# Draw a closed five-point star.
def draw_star(size):
    for point in range(5):
        turtle.forward(size)
        turtle.right(144)

# Draw the stage badge.
draw_star(80)
turtle.done()
