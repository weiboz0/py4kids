# Bring in Python's turtle drawing tools.
import turtle

squares = 8
side = 40
turned = 0
count = 0

for i in range(squares):
    if i % 3 == 0:
        turtle.pencolor("red")
    elif i % 3 == 1:
        turtle.pencolor("blue")
    else:
        turtle.pencolor("green")
    for corner in range(4):
        turtle.forward(side)
        turtle.left(90)
    turtle.left(45)
    turned = turned + 45
    count = count + 1

print(f"Turned: {turned}")
print(f"Squares: {count}")
turtle.done()
