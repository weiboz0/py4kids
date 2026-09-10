import turtle


turtle.color("teal")
turtle.pendown()

stamp_count = 4
size = 20
gap = 15

for stamp_number in range(stamp_count):
    turtle.pensize(stamp_number + 1)
    for side in range(4):
        turtle.forward(size)
        turtle.right(90)
    turtle.penup()
    turtle.forward(size + gap)
    turtle.pendown()

turtle.penup()
turtle.backward(stamp_count * (size + gap))
turtle.pendown()

turtle.done()
