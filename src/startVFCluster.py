from base.server.tcpserver import TCPServer, TCPRequestHandler
from adexchange.adexchange import AdExchange
from adexchange.seller import Seller
from adexchange.dbConnection import DBConnection
from settings import SERVER_BINDING, ADEX, TEST_PARAMS, SELLER
from common import get_logger
from math import floor
from random import randint

def init_cluster(bindings_list, object_constructor):
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

def get_leader(raft_objects):
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
    # initialize logging
    logger = get_logger("main")

    server = TCPServer((SERVER_BINDING['address'], int(SERVER_BINDING['port'])), TCPRequestHandler)

    # initialize adExObjects
    adExObjects = init_cluster(ADEX['bindings'], AdExchange)
    server.adExObject = get_leader(adExObjects)

    # initialize Seller object and populate seller info
    sellerObjects = init_cluster(SELLER['bindings'], Seller)
    server.sellerObject = get_leader(sellerObjects)
    server.sellerObject.populateSellerInfo()

    # initialize DB connection
    server.dbConnection = DBConnection()

    server.floodlightConnection = None
    server.mininetConnection = None

    if TEST_PARAMS['infra_tested'] == "MININET":
        server.floodlightConnection = FloodlightConnection(MININET_PARAMS['floodlight_host'], \
                                                               MININET_PARAMS['floodlight_username'], \
                                                               MININET_PARAMS['floodlight_password'], \
                                                               MININET_PARAMS['floodlight_log_file'], \
                                                               MININET_PARAMS['prompt'], \
                                                               MININET_PARAMS['floodlight_path'], \
                                                               MININET_PARAMS['circuit_pusher_port'])
        server.floodlightConnection.sshToVM()
        server.floodlightConnection.startFloodlightServer()

        server.mininetConnection = MininetConnection(MININET_PARAMS['mininet_host'], \
                                                         MININET_PARAMS['mininet_username'], \
                                                         MININET_PARAMS['mininet_password'], \
                                                         MININET_PARAMS['mininet_log_file'], \
                                                         MININET_PARAMS['prompt'], \
                                                         MININET_PARAMS['mininet_script_path'], \
                                                         MININET_PARAMS['mininet_script_file'])
        server.mininetConnection.sshToVM()
        server.mininetConnection.startMininetAPIServer()
        logger.info("\n> Connected to microdeployment testbed.")

    if ADEX['status'] == "open":
        server.serve_forever()
    elif ADEX['status'] == "closed":
        raise ValueError("AdExchange is currently closed and is not accepting requests.")
    else:
        raise ValueError("Unknown status. Check settings.")

if __name__ == '__main__':
    main()
