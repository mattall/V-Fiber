with open("mega_seller.txt",'w') as seller:
    seller.write("San Francisco, California; Denver, Colorado; 80000; 100; 850; Verizon; 66.180.55.0; 66.181.55.0\n")
    for x in range(80000):
        seller.write("{0};Gi 0/{0};Gi 0/{0}\n".format(x))
    seller.write("Kansas City, Missouri; Madison, Wisconsin; 100000; 100; 700; ATT; 192.168.1.0; 192.168.2.0\n")
    for x in range(100000):
        seller.write("{0};Gi 0/{0};Gi 0/{0}\n".format(x))
    seller.write("Salt Lake City, Utah; Kansas City, Missouri; 100000; 100; 700; ATT; 192.168.100.0/24; 192.168.101.0\n")
    for x in range(100000):
        seller.write("{0};Gi 0/{0};Gi 0/{0}\n".format(x))
    seller.write("Salt Lake City, Utah; Denver, Colorado; 80000; 100; 850; Cox; 64.170.55.0; 64.170.55.0\n")
    for x in range(80000):
        seller.write("{0};Gi 0/{0};Gi 0/{0}\n".format(x))
