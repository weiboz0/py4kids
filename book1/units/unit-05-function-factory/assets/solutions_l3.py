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
turtle.speed(0)

stamp(24)
stamp_gallery(3, 6)

turtle.done()


# Challenge 2 — the real drawing the notebook plan describes: a flower whose `petal`
# actually draws a closed shape, called once per loop turn. Run this file to see it.
def petal_shape(size):
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


def flower(size, petal_count):
    for petal_number in range(petal_count):
        petal_shape(size)
        turtle.right(360 / petal_count)


turtle.color("purple")
flower(30, 6)
turtle.done()
