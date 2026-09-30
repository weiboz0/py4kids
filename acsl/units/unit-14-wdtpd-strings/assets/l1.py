S = input()
n = int(input())
badge = S[:n] + S[len(S) - n:]
middle = S[n:len(S) - n]
print(badge, middle)
