score = int(input())
bonus = 0
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
    bonus = 5
elif score >= 70:
    grade = "C"
    bonus = 10
else:
    grade = "D"
if score + bonus >= 90:
    grade = grade + "+"
print(grade, score + bonus)
