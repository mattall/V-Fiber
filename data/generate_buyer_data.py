cities = ["A", "B", "C", "D", "E", "F", "G", "H"]

from itertools import combinations

x = 0
for c in combinations(cities, 2):
    with open('./circuit/circuitBuyers/circuitBuyer_{}.txt'.format(x), 'w') as fob:
        fob.write("{0}; {1}; 1; 1; 900; {0}_{1}".format(c[0], c[1]))
    x += 1

