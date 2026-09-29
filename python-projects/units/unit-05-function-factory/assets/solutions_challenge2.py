import turtle

# Challenge 2 solution — the flower the notebook plan describes, as a runnable drawing.
# `flower` calls `petal_shape` once per loop turn; neither function calls itself (no recursion).


def petal_shape(size):
    for edge in range(4):
        turtle.forward(size)
        turtle.right(90)


def flower(size, petal_count):
    for petal_number in range(petal_count):
        petal_shape(size)
        turtle.right(360 / petal_count)


turtle.color("purple")
turtle.pensize(2)

flower(30, 6)

# done() enters turtle's window loop and must be the LAST statement — no drawing after it.
turtle.done()
