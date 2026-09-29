def digits(n):
    if n < 10:
        return n
    return digits(n // 10) + 2 * (n % 10)


print(digits(4071))
