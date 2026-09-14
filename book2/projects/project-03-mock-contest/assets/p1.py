import sys

data = sys.stdin.read()
tokens = data.split()
idx = 0
n = int(tokens[idx]); idx = idx + 1
a = []
i = 0
while i < n:
    a.append(int(tokens[idx])); idx = idx + 1
    i = i + 1
pre = [0]
i = 0
while i < n:
    pre.append(pre[i] + a[i])
    i = i + 1
q = int(tokens[idx]); idx = idx + 1
out = ""
i = 0
while i < q:
    l = int(tokens[idx]); idx = idx + 1
    r = int(tokens[idx]); idx = idx + 1
    val = pre[r] - pre[l - 1]
    if len(out) > 0:
        out = out + " "
    out = out + str(val)
    i = i + 1
print(out)
