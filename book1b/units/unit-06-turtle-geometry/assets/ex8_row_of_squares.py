# Student task: replace the small placeholder with the drawing in Exercise 8.
import turtle

squares = 4
side = 40
travel = 60

# Draw one square per outer trip, travel after every square, then return with the pen lifted.
for corner in range(4):
    turtle.forward(10)
    turtle.left(90)

turtle.done()
