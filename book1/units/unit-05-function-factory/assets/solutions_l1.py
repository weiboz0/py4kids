import turtle


def stamp(size):
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


turtle.color("teal")
turtle.pensize(3)
turtle.speed(4)

for edge in range(2):
    turtle.forward(220)
    turtle.right(90)
    turtle.forward(140)
    turtle.right(90)

turtle.penup()
turtle.right(90)
turtle.forward(25)
turtle.left(90)
turtle.pendown()

for stamp_number in range(4):
    size = 18 + stamp_number * 4
    distance = stamp_number * 45
    turtle.penup()
    turtle.forward(distance)
    turtle.pendown()
    stamp(size)
    turtle.penup()
    turtle.backward(distance)
    turtle.pendown()

turtle.penup()
turtle.left(90)
turtle.forward(25)
turtle.right(90)
turtle.pendown()

turtle.done()
