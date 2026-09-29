x = int(input())
chain = str(x)
while x > 10:
    x = x - 3
    chain = chain + " " + str(x)
print(chain)
