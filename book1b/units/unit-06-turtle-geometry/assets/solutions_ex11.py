# Bring in Python's turtle drawing tools.
import turtle

side = 20
drawn = 0

for square in range(5):
    for corner in range(4):
        turtle.forward(side)
        turtle.left(90)
    side = side + 20
    drawn = drawn + 1

print(f"Squares: {drawn}")
turtle.done()
