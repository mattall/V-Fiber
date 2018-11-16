from base.server.tcpserver import TCPServer, TCPRequestHandler
from adexchange.adexchange import AdExchange
from adexchange.seller import Seller
from adexchange.dbConnection import DBConnection
from settings import SERVER_BINDING, ADEX, TEST_PARAMS, SELLER
from common import get_logger
from math import floor
from random import randint
from threading import Thread
from time import sleep
from argparse import ArgumentParser
from sys import exit
# from argparse.ArgumentParser import add_argument, parse_args

class VFiber(object):

    def __init__(self, id, cluster_size):
        self.__id = id
        bindings = 'bindings' + str(id)
        self.__logger = get_logger("main")
        try:
            server_addr = SERVER_BINDING['address'][id-1]
            self.server = TCPServer((SERVER_BINDING['address'][id-1], int(SERVER_BINDING['port'])), TCPRequestHandler)
        except Exception as e:
            print(e)
            self.__logger.debug("Server : {} ".format((id-1)))
            self.__logger.debug("Address: {}".format(SERVER_BINDING['address'][id-1]))
            self.__logger.debug("Port: {}", int(SERVER_BINDING['port']))
            exit()
        
        if cluster_size > 1:
            cluster_servers = SERVER_BINDING['address'][:cluster_size] 
            peers = cluster_servers[:]
            peers.remove(server_addr)
        
        elif cluster_size == 1: 
            peers = []

        exchangeID = server_addr + ':' + ADEX['port']
        exchangePeers = [ p + ':' + ADEX['port'] for p in peers ]
        try:
            self.server.adExObject = AdExchange(exchangeID, exchangePeers)
        except Exception as e:
            print(e)
            self.__logger.debug("Server Exchange ID: {}".format(exchangeID))
            self.__logger.debug("Peers : {}".format(exchangePeers))

        sellerID = server_addr + ':' + SELLER['port']
        sellerPeers = exchangePeers = [ p + ':' + SELLER['port'] for p in peers ]
        try:
            self.server.sellerObject = Seller(sellerID, sellerPeers)
        except Exception as e:
            print(e)
            self.__logger.debug("Server Seller ID: {}".format(SellerID))
            self.__logger.debug("Peers: {}".format(sellerPeers))

        self.server.sellerObject.populateSellerInfo()

    def init_cluster(self, bindings_list, object_constructor):
        '''
        (list_of_bindings, object_constructor) -> (list_of_servers)

        Takes a list of bindings and starts a raft server using each binding in the
        list.

        Returns a list of pointers to server objects.
        example..
            init_clister(list_of_bindings, obj_constructer)
        '''
        server_objects = []
        for address in bindings_list:
            partners = bindings_list[:]
            partners.remove(address)
            a_server = object_constructor(address, partners)
            server_objects.append(a_server)
        return server_objects

    def get_leader(self, raft_objects):
        '''
        (raft_objects) -> leader

        receives list of rafted objects, and returns a pointer to the leader.
        '''
        while True:
            test_leader = raft_objects[ randint(0, len(raft_objects) - 1) ]
            if test_leader._isLeader():
                leader = test_leader
                return leader


def main():
    parser = ArgumentParser()
    parser.add_argument('server_num', help="number 1,2,3... to distinguish whcih server is to begin running", type=int)
    parser.add_argument('total_servers', help="number 1,2,3... how many servers run in this cluster?", type=int)
    args = parser.parse_args()
    vFiber = VFiber(args.server_num, args.total_servers)

    if ADEX['status'] == "open":
        vFiber.server.serve_forever()
    elif ADEX['status'] == "closed":
        raise ValueError("AdExchange is currently closed and is not accepting requests.")
    else:
        raise ValueError("Unknown status. Check settings.")

if __name__ == '__main__':
    main()
