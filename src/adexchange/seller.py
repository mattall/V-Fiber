import gzip
from settings import CONTEXT, TEST_PARAMS, SELLER
import networkx as nx
from common import get_logger
from pysyncobj import SyncObj, replicated_sync, replicated, SyncObjConf
from threading import Lock

class Seller(SyncObj):
    def __init__(self, selfAddress, partnerAddresses):
        '''
        Initialize seller class
        '''
        cfg = SyncObjConf(logCompactionMinEntries = 2147483647, logCompactionMinTime = 2147483647)
        super(Seller, self).__init__(selfAddress, partnerAddresses, cfg)
        self.__rsp = TEST_PARAMS['server_path']
        self.__sf = TEST_PARAMS['seller_file_name']
        self.__compressed = CONTEXT['compressed_content']
        self.__sellerGraph = nx.Graph()
        self.__logger = get_logger("Seller")

    @replicated
    def populateSellerInfo(self):
        '''
        Populates seller graph with the seller information
        '''
        resource = []
        resource.append(self.__rsp)
        resource.append(self.__sf)
        zFile = None
        tFile = None

        if self.__compressed:
            zFile = gzip.open(''.join(resource)+".gz", "r+")
        else:
            zFile = open(''.join(resource), 'r')
        while True:
            line = zFile.readline()
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
                    if strands:
                        for x in range(strands):
                            line_str = zFile.readline()
                            line_str = line_str.strip()
                            strand_data = line_str.split(';')
                            interface_a = strand_data[1].strip()
                            interface_b = strand_data[2].strip()
                            interfaces.append((interface_a, interface_b))

                    self.__logger.debug("[TCPClient][run]Adding Link: {0}|{1} with {2} lambdas".format(point_A, point_B, len(interfaces)))
                    self.__sellerGraph.add_edge(point_A, point_B, \
                                                numberOfStrands = strands, \
                                                capacityPerStrand = strand_cap,\
                                                costPerStrand = strand_cost, \
                                                ISP = provider, prefixA = ip_A,\
                                                prefixB = ip_B,
                                                available_interfaces = interfaces, \
                                                unavailable_interfaces = []
                                                link_lock = Lock())
            else: # no line to read
                break

        zFile.close()
        self.__logger.info("### Seller Information populated...")

    def getSellerGraph(self):
        '''
        Returns a graph with all the seller information in it
        '''
        return self.__sellerGraph

    @replicated_sync
    def release_strand(self, u, v, num_to_release, local_lock_event, global_lock_event):
        try:
            local_lock = self.__sellerGraph[u][v]['link_lock'].aquire()
            local_lock_event.set()
            self.__logger.debug("Lock for {} {} aquired".format(u,v))
            global_lock_event.wait()

            # update edge info
            self.__sellerGraph[u][v]['numberOfStrands'] -= num_to_release

            # pop the number of requested interfaces (strands)
            buyer_interfaces = []
            for n in num_to_release:
                buyer_interfaces.append(self.__sellerGraph[u][v]['available_interfaces'].pop())

            self.__sellerGraph[u][v]['unavailable_interfaces'].extend(buyer_interfaces)

            # send list of two ip/port pairs for link
            resources = []
            for interface in buyer_interfaces:
                link_a = (self.__sellerGraph[u][v]['prefixA'], interface[0])
                link_b = (self.__sellerGraph[u][v]['prefixB'], interface[1])
                resources.extend((link_a, link_b))

        finally:
            local_lock.release()
        return resource

    @replicated_sync
    def release_strand_optimistic(self, u, v, num_to_release):
        # operate on copy of data. If data has changed before committing quit.

        # Returns if transaction completes, otherwise starts over.
        # Quits (Returns empty list) if insufficent resources are available.
        while True:
            strands_at_start = self.__sellerGraph[u][v]['numberOfStrands']
            copy_of_strands = strands_at_start[:]

            available_interfaces_at_start = self.__sellerGraph[u][v]['available_interfaces']
            ai_copy = available_interfaces_at_start[:]

            unavailable_interfaces_at_start = self.__sellerGraph[u][v]['unavailable_interfaces']
            ui_copy = unavailable_interfaces_at_start[:]

            proposed_number_of_strands = copy_of_strands - num_to_release

            # Get out of here if all strands have been used up.
            if proposed_number_of_strands < 0:
                return []

            buyer_interfaces = []
            for n in num_to_release:
                buyer_interfaces.append(ai_copy.pop())

            ui_copy.extend(buyer_interfaces)

            # Make changes and return if data hasn't changed since we got here.
            if strands_at_start == self.__sellerGraph[u][v]['numberOfStrands'] \
            and available_interfaces_at_start == self.__sellerGraph[u][v]['available_interfaces'] \
            and unavailable_interfaces_at_start == self.__sellerGraph[u][v]['unavailable_interfaces']:
                self.__sellerGraph[u][v]['numberOfStrands'] = proposed_number_of_strands
                self.__sellerGraph[u][v]['available_interfaces'] = ai_copy
                self.__sellerGraph[u][v]['unavailable_interfaces'] = ua_copy

                resources = []
                for interface in buyer_interfaces:
                    link_a = (self.__sellerGraph[u][v]['prefixA'], interface[0])
                    link_b = (self.__sellerGraph[u][v]['prefixB'], interface[1])
                    resources.extend((link_a, link_b))
                return resources
