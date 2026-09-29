import turtle


def stamp(size):
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


def stamp_gallery(rings, stamps_per_ring):
    for ring_number in range(rings):
        radius = 45 + ring_number * 25
        size = 18 + ring_number * 5
        for stamp_number in range(stamps_per_ring):
            turtle.penup()
            turtle.forward(radius)
            turtle.pendown()
            stamp(size)
            turtle.penup()
            turtle.backward(radius)
            turtle.pendown()
            turtle.right(360 / stamps_per_ring)
        turtle.right(360 / rings)


turtle.color("darkgreen")
turtle.pensize(2)

stamp(24)
stamp_gallery(3, 6)

turtle.done()

