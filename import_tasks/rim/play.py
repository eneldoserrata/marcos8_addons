
with open("clean.txt", "r") as lines:
    for line in lines:
        if len(line) == 3 or len(line) == 4:
            print line
