# Bring in the drawing and random-choice tools.
import turtle
import random

random.seed(4)

# turtle-check: open-path
# Take a fixed step, then randomly choose a left or right turn.
step = 31
move_count = 20
turtle.pencolor("seagreen")
turtle.pensize(3)

for move_number in range(move_count):
    turtle.forward(step)
    turn = random.randint(0, 1)
    if turn == 0:
        turtle.left(90)
    else:
        turtle.right(90)

turtle.done()
