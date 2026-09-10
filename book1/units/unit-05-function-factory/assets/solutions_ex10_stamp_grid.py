import turtle


def stamp(size):
    for side in range(4):
        turtle.forward(size)
        turtle.right(90)


turtle.color("royalblue")
turtle.pensize(2)
turtle.speed(0)
turtle.pendown()

rows = 3
columns = 4
size = 20
column_step = 35
row_step = 35
stamps_drawn = 0

for row_number in range(rows):
    for column_number in range(columns):
        stamp(size)
        stamps_drawn = stamps_drawn + 1
        turtle.penup()
        turtle.forward(column_step)
        turtle.pendown()

    turtle.penup()
    turtle.backward(columns * column_step)
    turtle.right(90)
    turtle.forward(row_step)
    turtle.left(90)
    turtle.pendown()

turtle.penup()
turtle.left(90)
turtle.forward(rows * row_step)
turtle.right(90)
turtle.pendown()

print(stamps_drawn)
turtle.done()
