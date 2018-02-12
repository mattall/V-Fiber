import datetime

def getTDelta(time2, time1):
    datetimeFormat = '%H:%M:%S:%f'
    tdelta = datetime.datetime.strptime(time1, datetimeFormat) - datetime.datetime.strptime(time2, datetimeFormat)
    return tdelta.seconds * 1000 + tdelta.microseconds/1000

def parseSpew(sFile):
    lines = []
    with open(sFile, "r") as sF:
        for line in sF:
            line = line.strip()
            if line.startswith("TIMESTAMP"):
                line = line[11:-1]
                timestamp, message = line.split(" ", 1)
                if ", " in message:
                    vals = message.split(",")
                    for v in vals:
                        lines.append((timestamp, v.strip().lower()))
                else:
                    lines.append((timestamp, message.lower()))

    for l in lines:
        print l

    lines = sorted(lines, key=lambda lines: lines[1].rsplit(" ")[0])
    index = 0
    for a, b in zip(lines[::2], lines[1::2]):
        key = a[1].rsplit(" ", 1)[0]
        if "reservesharedbandwidth" in a[1] and "reservesharedbandwidth" in b[1]:
            # print "{0} takes {1}ms".format(key, getTDelta(a[0], b[0]))
            print "{0},{1},{2},OK".format(key, a[0], b[0])
            continue
        if index == 0:
            print "{0}_{1},{2},{3},OK".format(key, index, a[0], b[0])
            index = 1
        else:
            print "{0}_{1},{2},{3},OK".format(key, index, a[0], b[0])
            index = 0

if __name__ == "__main__":
    # parseSpew("spewlogfile.txt")
    parseSpew("spewlogfile-overhead.txt")
