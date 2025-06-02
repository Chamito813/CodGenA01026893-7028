r = 10
i=0

while i < 10:
    i = i + 1
    if i < 5:
        r = r + 25
    elif i == 5:
        r = r - 35
    else:
        r = r - 1

print(r)