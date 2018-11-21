from sys import exit
from ipaddress import IPv4Address
from itertools import combinations

seller_data = []

node = {}
edge = set()
base_addr = IPv4Address(u'127.0.0.2')
address = {}


with open("./darkStrand/darkStrandMap.txt", 'r') as fob:
    line = fob.readline()
    while line:
        if "node [" in line:
            id = 0
            loc = ""
            while "]" not in line:
                if 'id' in line:
                    id = int(line.split()[1])
                if 'label' in line:
                    loc = line.split()[1:]
                    loc =''.join(loc)
                    loc = loc[1:-1]
                line = fob.readline()
            node[id] = loc
            address[node[id]] = base_addr + id

        if "edge [" in line:
            source = ''
            target = ''
            while "]" not in line:
                if "source" in line:
                    source = int(line.split()[1])
                    source = node[source]
                    
                if "target" in line:
                    target = int(line.split()[1])
                    target = node[target]

                line = fob.readline()
            edge.add((source, target))
        
        line = fob.readline()

# for n in range(len(node)):
#     print(node[n])
# print(node.keys())
# for e in edge:
#     print(e)

# for a in address:
#     print(a, str(address[a]))


with open("./darkStrand/darkStrandSeller.txt", 'w') as sFile:
    for e in edge:
        sFile.write("{}; {}; 40; 1; 100; DarkStrand; {}; {}\n"\
            .format(e[0], e[1], str(address[e[0]]), str(address[e[1]])))
        for x in range(40):
            sFile.write("{0}; Gi 0/{0}; Gi 0/{0}\n".format(x))

clients = []
i = 0
for c in combinations(node.values(),2):
    with open("./darkStrand/darkStrandBuyers/darkStrandBuyer_{}.txt".format(i), 'w') as bFile:
        bFile.write("{0}; {1}; {2}; {3}; {4}; {0}_{1}"\
            .format(c[0], c[1], 1, 1, 900))
    i += 1
