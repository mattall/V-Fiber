from settings import CONTEXT, TEST_PARAMS
import networkx as nx
from netaddr import IPNetwork, IPAddress
from collections import defaultdict

class Layer3(object):
    def __init__(self):
        '''
        Initialize seller class
        '''
        self.__rsp = TEST_PARAMS['path']
        self.__sf = TEST_PARAMS['seller_file_name']
        self.__compressed = CONTEXT['compressed_content']
        self.__isdebug = CONTEXT['debug']
        self.__sellerGraph = None
        self.__allocation = None
        self.__dbConnection = None
        self.__finalList = []

    def getProviderAndPrefix(self, allocation, sellerGraph):
        path = nx.shortest_path(sellerGraph, source=allocation.linkA, target=allocation.linkB)
        tuples = []
        for (u,v) in zip(path[0:], path[1:]):
            tuples.append((sellerGraph[u][v]['ISP'], sellerGraph[u][v]['prefixA'], sellerGraph[u][v]['prefixB']))
        return tuples

    def addr(self, address, prefix):
        ip = IPNetwork(address)
        ip.prefixlen = int(prefix)
        return ip

    def getIPAddresses(self, pt, nOS, cName, dbConn):
        networkA, maskA = pt[1].split("/")
        networkB, maskB = pt[2].split("/")

        cursor = dbConn.query("select INET_NTOA(IPAddressA) as IPAddressB, INET_NTOA(IPAddressB) as IPAddressB, \
                              PortA, PortB from VirtualFiber.IPAllocation where PrefixA='%s' and PrefixB='%s'" % (pt[1], pt[2]))
        result = cursor.fetchall()
        if len(result) == 0:
            # first time a prefix is seen
            # generate nOS IP addresses and updateDB
            ipIterA = self.addr(networkA, maskA)
            ipIterB = self.addr(networkB, maskB)
            ipGenA = ipIterA.iter_hosts()
            ipGenB = ipIterB.iter_hosts()
            portListA = [str(i+1) for i in range(nOS)]
            portListB = [str(i+1) for i in range(nOS)]

            ipAddrListA = list(str(next(ipGenA)) for _ in range(nOS))
            ipAddrListB = list(str(next(ipGenB)) for _ in range(nOS))
            for ipA, ipB, portA, portB in zip(ipAddrListA, ipAddrListB, portListA, portListB):
                dbConn.query("INSERT INTO `VirtualFiber`.`IPAllocation` \
                             (`ClientName`, `PrefixA`, `IPAddressA`, \
                                            `PrefixB`, `IPAddressB`, \
                                            `PortA`, `PortB`) \
                             VALUES('%s','%s',INET_ATON('%s'),'%s',INET_ATON('%s'),%d,%d)" % \
                             (cName, pt[1], ipA, pt[2], ipB, int(portA), int(portB)))
            return (ipAddrListA, ipAddrListB, portListA, portListB)
        else:
            # Some IPs assigned already assigned in prefix. Generate new unallocated
            lastBigAddressA = result[-1][0]
            lastBigAddressB = result[-1][1]
            lastBigPortA = result[-1][2]
            lastBigPortB = result[-1][3]

            ipBigA = int(IPAddress(lastBigAddressA))
            ipBigB = int(IPAddress(lastBigAddressB))
            ipListA = []
            ipListB = []
            portListA = []
            portListB = []
            for i in xrange(nOS):
                newIPA = ipBigA+i+1
                newIPB = ipBigB+i+1
                newPortA = lastBigPortA+i+1
                newPortB = lastBigPortB+i+1
                dbConn.query("INSERT INTO `VirtualFiber`.`IPAllocation` \
                            (`ClientName`, `PrefixA`, `IPAddressA`,  \
                                           `PrefixB`, `IPAddressB`,  \
                                           `PortA`, `PortB`)         \
                            VALUES('%s','%s',%d,'%s',%d,%d,%d)" % (cName, pt[1], newIPA, pt[2], newIPB, newPortA, newPortB))
                ipListA.append(str(IPAddress(newIPA)))
                ipListB.append(str(IPAddress(newIPB)))
                portListA.append(str(newPortA))
                portListB.append(str(newPortB))
            return (ipListA, ipListB, portListA, portListB)

    def allocateIPAddresses(self, sellerGraph, allocation, dbConnection):
        '''
        Populates seller graph with the seller information
        and request allocations done
        '''
        self.__sellerGraph = sellerGraph
        self.__allocation = allocation
        self.__dbConnection = dbConnection
        self.__finalList = []

        recordsDict = defaultdict(list)
        for allocation in self.__allocation:
            if allocation.winnerFlag == 1:
                # get provider and prefix
                providerTuples = self.getProviderAndPrefix(allocation, self.__sellerGraph)
                # generate new IP addresses for the allocation  based on numberOfStrands
                for pt in providerTuples:
                    (ipAddressesA, ipAddressesB, portsA, portsB) = self.getIPAddresses(pt, allocation.numberOfStrands, \
                                                                                       allocation.clientName, self.__dbConnection)
                    recordsDict[allocation.clientName].append((','.join(ipAddressesA), ','.join(ipAddressesB), \
                                                               pt[0], pt[1], pt[2], ','.join(portsA), ','.join(portsB)))

        for key in recordsDict.keys():
            for alloc in self.__allocation:
                if alloc.clientName == key:
                    print alloc.prefixA, alloc.prefixB
                    tempPrefix_A = []
                    tempPrefix_B = []
                    tempIP_A = []
                    tempIP_B = []
                    tempPort_A = []
                    tempPort_B = []
                    tempISP = []
                    for rr in recordsDict[key]:
                        tempIP_A.append(rr[0])
                        tempIP_B.append(rr[1])
                        tempISP.append(rr[2])
                        tempPrefix_A.append(rr[3])
                        tempPrefix_B.append(rr[4])
                        tempPort_A.append(rr[5])
                        tempPort_B.append(rr[6])

                    t1 = alloc._replace(ipA = ','.join(tempIP_A), \
                                        ISP = ','.join(tempISP), \
                                        ipB = ','.join(tempIP_B), \
                                        prefixA = ','.join(tempPrefix_A), \
                                        prefixB = ','.join(tempPrefix_B), \
                                        portA = ','.join(tempPort_A), \
                                        portB = ','.join(tempPort_B))
                    self.__finalList.append(t1)

        return self.__finalList
