bidderID = raw_input("Enter ID again to confirm:")
f = open("userInfo.LazyCat", "r")
lines = f.readlines()
f.close()
alllines = iter(lines)
f = open("userInfo.LazyCat","w")
for line in alllines:
    if line != bidderID + '\n':
        f.write(line)
    else:
        next(alllines, None)
        next(alllines, None)
        next(alllines, None)
        next(alllines, None)
        continue
f.close()
