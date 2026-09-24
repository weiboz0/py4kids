# Bring in Python's turtle drawing tools.
import turtle

rows = 3
columns = 3
side = 30
travel = 45
squares = 0

for row in range(rows):
    for column in range(columns):
        for corner in range(4):
            turtle.forward(side)
            turtle.left(90)
        squares = squares + 1
        turtle.penup()
        turtle.forward(travel)
        turtle.pendown()
    # Return to the row start before moving up to the next row.
    turtle.penup()
    turtle.backward(columns * travel)
    if row < rows - 1:
        turtle.left(90)
        turtle.forward(travel)
        turtle.right(90)
    else:
        turtle.left(90)
        turtle.backward((rows - 1) * travel)
        turtle.right(90)
    turtle.pendown()

print(f"Squares: {squares}")
turtle.done()
