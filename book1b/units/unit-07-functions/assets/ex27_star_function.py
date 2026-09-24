# Student task: change this working square into the Exercise 27 star.
import turtle


# Start with a small closed outline; change its loop to draw the star.
def draw_star(size):
    for point in range(4):
        turtle.forward(size)
        turtle.right(90)


turtle.pencolor("gray")
draw_star(24)

turtle.done()
