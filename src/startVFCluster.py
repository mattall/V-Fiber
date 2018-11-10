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
        self.logger = get_logger("main")
        try:
            server_addr = SERVER_BINDING['address'][id-1]
            self.server = TCPServer((SERVER_BINDING['address'][id-1], int(SERVER_BINDING['port'])), TCPRequestHandler)
        except Exception as e:
            print(e)
            print("SERVER_BINDING['address'][id-1]", SERVER_BINDING['address'][id-1])
            print("int(SERVER_BINDING['port']", int(SERVER_BINDING['port']))
            exit()
        
        
        cluster_servers = SERVER_BINDING['address'][:cluster_size] 
        peers = cluster_servers[:]
        peers.remove(server_addr)

        exchangeID = server_addr + ':' + ADEX['port']
        exchangePeers = [ p + ':' + ADEX['port'] for p in peers ]
        self.server.adExObject = AdExchange(exchangeID, exchangePeers)

        sellerID = server_addr + ':' + SELLER['port']
        sellerPeers = exchangePeers = [ p + ':' + SELLER['port'] for p in peers ]
        self.server.sellerObject = Seller(SELLER[bindings][0], SELLER[bindings][1:])

        self.server.sellerObject.populateSellerInfo()

    # def __adex_leader_daemon(self):
    #     while True:
    #         if self.server.adExObject._isLeader():
    #             pass
    #         else:
    #             self.server.adExObject = self.get_leader(self.adExObjects)
    #
    # def __seller_leader_daemon(self):
    #     while True:
    #         if self.server.adExObject._isLeader():
    #             pass
    #         else:
    #             self.server.adExObject = self.get_leader(self.adExObjects)

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
