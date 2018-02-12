with open('userInfo.LazyCat', 'r') as infile:
    data = infile.read()
my_list = data.splitlines()
i = 1

for line in my_list:
    if i % 4 == 3:
        print "User from \t%s" % line
    elif i % 4 == 0:
        print "Name \t\t%s\n" % line
    elif i % 4 == 1:
        print "BidderID \t%s" % line
    i += 1

infile.close()
