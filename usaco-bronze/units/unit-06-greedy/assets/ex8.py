import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
segments = []
i = 0
while i < n:
    start = int(parts[i * 2 + 1])
    end = int(parts[i * 2 + 2])
    segments.append((start, end))
    i = i + 1

def segment_end(segment):
    return segment[1]

segments = sorted(segments, key=segment_end)
checkpoint = -1
checkpoint_count = 0
i = 0
while i < n:
    start = segments[i][0]
    end = segments[i][1]
    if checkpoint < start:
        checkpoint = end
        checkpoint_count = checkpoint_count + 1
    i = i + 1
print(str(checkpoint_count))
