'''
This script reads data from the sellerData.txt file and generates requests
for resources in that file.
'''

import pandas as pd
import random as rand

# Get seller information
sellers = pd.read_csv("sellerData.txt", sep=';')
sources = sellers['#LinkA']
destinations = sellers['LinkB']

# Get request file ready
requests = int(raw_input("How many requests should we make?\n> "))
print("requests: {}".format(requests))

filename = "clientRequests_{}".format(requests)

with open(filename, "w") as requestFile:
    for r in xrange(requests):
        print("r = {}".format(r))
        source = rand.choice(sources)
        dest = rand.choice(destinations)
        strands = rand.randint(1, 10)
        capacity = rand.randint(1, 100)
        bid = rand.randint(600, 1000)

        request = "{};{};{};{};{}\n".format(source, dest, strands, capacity, bid, r)
        print("Writing request {}: ".format(request))
        requestFile.write(request)
