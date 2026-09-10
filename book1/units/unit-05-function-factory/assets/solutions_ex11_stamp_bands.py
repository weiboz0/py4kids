import turtle


def stamp(size):
    for side in range(4):
        turtle.forward(size)
        turtle.right(90)


turtle.color("darkorange")
turtle.pensize(2)
turtle.speed(0)
turtle.pendown()

bands = 2
stamps_per_band = 5
band_step = 50
stamps_drawn = 0

for band_number in range(bands):
    size = 15 + band_number * 5
    stamp_step = size + 10

    for stamp_number in range(stamps_per_band):
        stamp(size)
        stamps_drawn = stamps_drawn + 1
        turtle.penup()
        turtle.forward(stamp_step)
        turtle.pendown()

    turtle.penup()
    turtle.backward(stamps_per_band * stamp_step)
    turtle.right(90)
    turtle.forward(band_step)
    turtle.left(90)
    turtle.pendown()

turtle.penup()
turtle.left(90)
turtle.forward(bands * band_step)
turtle.right(90)
turtle.pendown()

print(stamps_drawn)
turtle.done()
