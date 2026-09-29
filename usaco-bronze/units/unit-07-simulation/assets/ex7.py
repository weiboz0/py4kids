import sys

data = sys.stdin.read()
parts = data.split()
card_count = int(parts[0])
ali_score = 0
bo_score = 0
current_player = 0
i = 0
while i < card_count:
    card = int(parts[i + 1])
    if current_player == 0:
        ali_score = ali_score + card
    else:
        bo_score = bo_score + card
    if card % 2 == 1:
        if current_player == 0:
            current_player = 1
        else:
            current_player = 0
    i = i + 1
if ali_score > bo_score:
    print("ALI")
elif bo_score > ali_score:
    print("BO")
else:
    print("TIE")
