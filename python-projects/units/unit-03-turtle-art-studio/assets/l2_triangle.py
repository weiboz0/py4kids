# Drawing tools from Python's turtle.
import turtle

# Three sides. A triangle turns 120 degrees at each corner.
angle = 120
for side in range(3):
    turtle.forward(100)
    turtle.right(angle)

turtle.done()
