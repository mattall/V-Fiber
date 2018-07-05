file_ob = open("labSeller.txt", "r")

while True:
    line = file_ob.readline()
    if line:
        if line.startswith("#"): continue
        line = line.strip()
        vals = line.split(";")
        if len(vals) == 8:
            point_A = vals[0].strip()
            point_B = vals[1].strip()
            strands = int(vals[2])
            strand_cap = int(vals[3])
            strand_cost = int(vals[4])
            provider = vals[5].strip()
            ip_A = vals[6].strip()
            ip_B = vals[7].strip()
            interfaces = []
            print "Printing vals" + str(vals)

            if strands:
                for x in range(strands):
                    line_str = file_ob.readline()
                    line_str = line_str.strip()
                    strand_data = line_str.split(';')
                    if len(strand_data) != 3:
                        print("ERROR: reading bad line for strand_data")
                        print("Strand_data = " + strand_data)

                    interface_a = strand_data[1].strip()
                    interface_b = strand_data[2].strip()
                    interfaces.append((interface_a, interface_b))
            print "printing interfaces" + str(interfaces)
    else:
        break
