# Bring in Python's turtle drawing tools.
import turtle

points = 7
side = 90

# Keep the true fractional turn so all seven strokes close the star.
for point in range(points):
    turtle.forward(side)
    turtle.left(3 * 360 / 7)

turtle.done()
