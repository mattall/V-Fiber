from seller import Seller
from settings import CONTEXT, ADEX
from gsp import GSP
from vcg import VCG
import networkx as nx
from common import get_logger
from pysyncobj import SyncObj, replicated, SyncObjConf
from threading import Thread, Event
from multiprocessing.pool import ThreadPool

class AdExchange(SyncObj):
    def __init__(self, selfAddress, partnerAddresses):
        '''
        Add connection object here if exchange is physically located in a separate server
        '''
        cfg = SyncObjConf(logCompactionMinEntries = 2147483647, logCompactionMinTime = 2147483647)
        super(AdExchange, self).__init__(selfAddress, partnerAddresses, cfg)
        self.__logger = get_logger("AdExchange")
        self.__logger.info("### Starting Ad Exchange...")
        self.__auction = ADEX['auction']
        self.__reserve = ADEX['reserve']

    def availableAttributes(self, path, G):
        return [(u, v, G[u][v]['numberOfStrands'], G[u][v]['capacityPerStrand'], \
                       G[u][v]['costPerStrand'], G[u][v]['ISP'], G[u][v]['prefixA'], G[u][v]['prefixB']\
                 ) for (u,v) in zip(path[0:],path[1:])]

    def updateSellerGraph_and_getResources(self, S, links_in_path, total_links, reqValues):
        ip_port_pairs = []

        ## Two phase commit
        if total_links > 1:
            # create empty list of lock aquire events.
            lock_aquire_events = []

            # set this event when all locks are aquired
            all_locks_aquired = Event()

            # concurrency object for getting return value from parallel threads
            pool = ThreadPool(processes = total_links)
            threads = []

            for (u,v) in links_in_path:
                # set up event for link
                lock_aquire_event = Event()
                lock_aquire_events.apped(lock_aquire_event)

                # start client threads
                for item in reqValues:
                    ### if code gets stuck here try apply_async
                    release_strand_thread = pool.apply(
                                            name="release_strand:{}_{}".format(u,v),
                                            target=S.release_strand,
                                            args=(u,v,item.numberOfStrands,
                                            lock_aquire_event, all_locks_aquired,))

                    threads.append(release_strand_thread)

            # when all lock_aquire_events are set, set all_locks_aquired
            for e in lock_aquire_events:
                while not e.isSet():
                    event_is_set = e.wait()
            all_locks_aquired.set()

            # get resulting ip_port_pairs
            for t in threads:
                t.join()
                ip_port_pairs.extend(t.get())


        ## Optimistic CC
        elif total_links == 1:
            for (u,v) in links_in_path:
                for item in reqValues:
                    ip_port_pairs.extend(S.release_strand_optimistic(u, v, item.numberOfStrands))

        else:
            self.__logger.info("ERROR! Impssible number of links given.")

        return ip_port_pairs

    def resourceAvailable(self, G, path, reqValues):
        pathHasCapacity = True
        pathHasStrands = True
        for (u,v) in zip(path[0:], path[1:]):
            for item in reqValues:
                if G[u][v]['numberOfStrands'] < item.numberOfStrands:
                    pathHasStrands = False
                if G[u][v]['capacityPerStrand'] < item.capacityPerStrand:
                    pathHasCapacity = False
        if pathHasStrands and pathHasCapacity:
            return True
        else:
            return False

    def getCostOfPath(self, path, G):
        cost = 0
        for (u,v) in zip(path[0:], path[1:]):
            cost += G[u][v]['costPerStrand']
        return cost

    def linksInPath(self, path):
        return zip(path[0:], path[1:])


    def updateRequestList(self, reqList, allocationDict):
        newReqList = []
        for k, v in reqList.items():
            for item in v:
                cName = item.clientName
                if (cName in allocationDict.keys()):
                    # namedtuple is immutable, so a hacky way to create the mutable effect
                    t1 = item._replace(winnerFlag = 1)
                    t2 = t1._replace(toPay = allocationDict[cName])
                    newReqList.append(t2)
                else:
                    newReqList.append(item)
        return newReqList

    def runVickreyAuction(self, reqList, sellerGraph):
        '''
        Function to call VCG mechanism
        '''
        allocation = []
        self.__logger.debug("[AdExchange][runVickreyAuction]")
        self.__logger.debug("Allocation decisions.")

        allocationDict = {}
        for key, v in reqList.items():
            k1,k2=key.split("#")
            # n denotes the number of customers bidding for that conduit
            n = len(v)
            slot_click = [1] * n

            shortestPath = nx.shortest_path(sellerGraph, source=k1, target=k2)
            gCoP = self.getCostOfPath(shortestPath, sellerGraph)
            lIP = self.linksInPath(shortestPath)
            k = len(lIP)
            reserve = max(self.__reserve, gCoP/k)

            bids = []
            for item in v:
                bids.append((item.clientName, item.bidPerStrand))

            if nx.has_path(sellerGraph, k1, k2) and self.resourceAvailable(sellerGraph, shortestPath, v):
                (alloc, payments) = VCG.compute(slot_click, reserve, bids)
                allocation.extend(zip(alloc, [i * k for i in payments]))
                for (kTest, vTest) in allocation:
                    allocationDict[kTest] = vTest

                # Updates sellerGraph with the allocation
                self.__logger.debug("Before > {}".format(self.availableAttributes(shortestPath, sellerGraph)))
                ip_port_pairs = self.updateSellerGraph_and_getResources(sellerGraph, shortestPath, v)
                self.__logger.debug("After > {}".format(self.availableAttributes(shortestPath, sellerGraph)))
            else:
                self.__logger.info("Link does not exists between {} and {}".format(k1, k2))
        return (self.updateRequestList(reqList, allocationDict), ip_port_pairs)

    def runSecondPriceAuction(self, reqList, seller):
        '''
        Function to call GSP mechanism
        '''
        sellerGraph = seller.getSellerGraph()

        allocation = []
        self.__logger.debug("[AdExchange][runSecondPriceAuction]")
        self.__logger.debug("Fiber allocation decisions.")

        allocationDict = {}
        ip_port_pairs = []
        for key, v in reqList.items():
            k1,k2=key.split("#")
            # n denotes the number of customers bidding for that conduit
            n = len(v)
            slot_click = [1] * n

            try:
                shortestPath = nx.shortest_path(sellerGraph, source=k1, target=k2)
                gCoP = self.getCostOfPath(shortestPath, sellerGraph)
                lIP = self.linksInPath(shortestPath)
                num_links = len(lIP)
                reserve = max(self.__reserve, gCoP/num_links)

                bids = []
                for item in v:
                    bids.append((item.clientName, item.bidPerStrand))

                if nx.has_path(sellerGraph, k1, k2) and self.resourceAvailable(sellerGraph, shortestPath, v):
                    (alloc, payments) = GSP.compute(slot_click, reserve, bids)
                    allocation.extend(zip(alloc, [i * num_links for i in payments]))
                    for (kTest, vTest) in allocation:
                        allocationDict[kTest] = vTest

                    # Updates sellerGraph with the allocation
                    self.__logger.debug("Before > {}".format(self.availableAttributes(shortestPath, sellerGraph)))
                    ip_port_pairs = self.updateSellerGraph_and_getResources(seller, lIP, num_links, v)
                    self.__logger.debug("After > {}".format(self.availableAttributes(shortestPath, sellerGraph)))
                else:
                    self.__logger.info("Link does not exists between {} and {}. No resource available for request".format(k1, k2))
            except nx.NodeNotFound:
                self.__logger.info("Path does not exists between {} and {}. No resource available for request".format(k1, k2))
                allocationDict = {}
                break;
        return (self.updateRequestList(reqList, allocationDict), ip_port_pairs)

    def processClientRequests(self, reqList, sellerObj):
        '''
        Function to dispatch client request to the corresponding auction mechanism
        '''
        self.__logger.debug("[AdExchange][processClientRequest]Request List: {}".format("|".join(reqList)))
        self.__logger.debug("[AdExchange][processClientRequest]Seller List (locations): {}".format("|".join(sellerObj.getSellerGraph())))
        self.__logger.debug("[AdExchange][processClientRequest]Auction Type: {}".format(self.__auction))
        self.__logger.debug("[AdExchange][processClientRequest]Reserve Price: {}".format(self.__reserve))


        # print request list
        for k, v in reqList.items():
            for item in v:
                self.__logger.info(item)

        # check for auction type and call the corresponding functions
        if self.__auction == "vcg":
            return self.runVickreyAuction(reqList, sellerObj)
        elif self.__auction == "gsp":
            return self.runSecondPriceAuction(reqList, sellerObj)
        else:
            raise ValueError("Unknown auction type. Either use 'vcg' or 'gsp' in settings.")
