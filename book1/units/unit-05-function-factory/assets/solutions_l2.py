import turtle


def polygon_points(n):
    return 360 / n


def polygon(n, side_length):
    turn_angle = polygon_points(n)
    for side in range(n):
        turtle.forward(side_length)
        turtle.right(turn_angle)


turtle.color("purple")
turtle.pensize(3)
turtle.speed(4)

polygon(3, 90)
turtle.right(120)
polygon(4, 70)
turtle.right(120)
polygon(5, 55)
turtle.right(120)

turtle.done()
