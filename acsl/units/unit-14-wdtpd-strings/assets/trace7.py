S = "ABRACADABRA"
same = 0
diff = 0
for j in range(len(S) // 2):
    if S[j] == S[len(S) - 1 - j]:
        same = same + 1
    else:
        diff = diff + 1
print(same, diff)
