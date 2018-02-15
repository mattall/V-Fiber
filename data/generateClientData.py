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

filename = "clientRequests_{}.txt".format(requests)

with open(filename, "w") as requestFile:
    heading = "#{:26}|{:27}|{:3}|{:8}|{:5}|{:3}\n#".format("Source", "Destination", "Total Strands", "Capacity", "Bid", "Client")
    requestFile.write(heading)
    requestFile.write("="*len(heading)+"\n")
    for r in xrange(requests):
        source = rand.choice(sources)
        dest = rand.choice(destinations)
        while dest.strip() == source.strip():
            dest = rand.choice(destinations)
        strands = rand.randint(1, 10)
        capacity = rand.randint(1, 100)
        bid = rand.randint(600, 1000)

        request = "{:27};{:27};{:13};{:8};{:5};{:6}\n".format(source, dest, strands, capacity, bid, r)
        requestFile.write(request)
