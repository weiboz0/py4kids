import turtle


turtle.color("teal")
turtle.pensize(3)
turtle.speed(0)
turtle.pendown()

stamp_count = 4
size = 20
gap = 15

for stamp_number in range(stamp_count):
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
