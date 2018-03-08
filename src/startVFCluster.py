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

class VFiber(object):

    def __init__(self):
        self.logger = get_logger("main")
        self.server = TCPServer((SERVER_BINDING['address'], int(SERVER_BINDING['port'])), TCPRequestHandler)
        # self.adExObjects = self.init_cluster(ADEX['bindings'], AdExchange)
        # self.server.adExObject = self.get_leader(self.adExObjects)
        self.server.adExObject = AdExchange(ADEX['bindings'][0], ADEX['bindings'][1:])

        # self.sellerObjects = self.init_cluster(SELLER['bindings'], Seller)
        # self.server.sellerObject = self.get_leader(self.sellerObjects)
        self.server.sellerObject = Seller(SELLER['bindings'][0], SELLER['bindings'][1:])
        self.server.sellerObject.populateSellerInfo()


        # # Create Daemon process for keeping leader current.
        # self.adex_leader_daemon = Thread(target = self.__adex_leader_daemon)
        # self.adex_leader_daemon.setDaemon(True)
        # self.adex_leader_daemon.start()
        #
        # self.seller_leader_deamon = Thread(target = self.__seller_leader_daemon)
        # self.seller_leader_deamon.setDaemon(True)
        # self.seller_leader_deamon.start()

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
    vFiber = VFiber()

    if ADEX['status'] == "open":
        vFiber.server.serve_forever()
    elif ADEX['status'] == "closed":
        raise ValueError("AdExchange is currently closed and is not accepting requests.")
    else:
        raise ValueError("Unknown status. Check settings.")

if __name__ == '__main__':
    main()
