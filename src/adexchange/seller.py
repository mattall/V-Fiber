import gzip
from settings import CONTEXT, TEST_PARAMS, SELLER
import networkx as nx
from common import get_logger
from pysyncobj import SyncObj, replicated_sync, replicated

class Seller(SyncObj):
    def __init__(self, selfAddress, partnerAddresses):
        '''
        Initialize seller class
        '''
        super(Seller, self).__init__(selfAddress, partnerAddresses)
        self.__rsp = TEST_PARAMS['path']
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
            for line in zFile.readlines():
                if line.startswith("#"): continue
                line = line.strip()
                vals = line.split(";")
                self.__sellerGraph.add_edge(vals[0].strip(),vals[1].strip(),numberOfStrands=int(vals[2]), \
                                            capacityPerStrand=int(vals[3]), costPerStrand=int(vals[4]), \
                                            ISP=vals[5].strip(), prefixA=vals[6].strip(), prefixB=vals[7].strip())
            zFile.close()
        else:
            tFile = open(''.join(resource), 'r')
            for line in tFile.readlines():
                if line.startswith("#"): continue
                line = line.strip()
                vals = line.split(";")
                self.__sellerGraph.add_edge(vals[0].strip(),vals[1].strip(),numberOfStrands=int(vals[2]), \
                                            capacityPerStrand=int(vals[3]), costPerStrand=int(vals[4]), \
                                            ISP=vals[5].strip(), prefixA=vals[6].strip(), prefixB=vals[7].strip())
            tFile.close()
        self.__logger.info("### Seller Information populated...")

    def getSellerGraph(self):
        '''
        Returns a graph with all the seller information in it
        '''
        return self.__sellerGraph

    @replicated_sync
    def release_strand(self, u, v, num_to_release):
        self.__sellerGraph[u][v]['numberOfStrands'] -= num_to_release
