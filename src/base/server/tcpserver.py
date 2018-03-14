import SocketServer, time, gzip, sys, collections
from SocketServer import BaseRequestHandler
from base.model.datamodel import Request, Data, Utility
from adexchange.adexchange import AdExchange
from adexchange.seller import Seller
from adexchange.layer3 import Layer3
from adexchange.dbConnection import DBConnection
from settings import CONTEXT, SERVER_BINDING, DB_PARAMS, TEST_PARAMS
from collections import defaultdict
from common import get_logger, Timer
#from realdeployment.configureTestbedAndCircuit import two_nodes_rspec_simple
from realdeployment.lab_testbed import addLink
#from realdeployment.ExperimentOverhead.plotTimeline import *
from subprocess import call
from StringIO import StringIO
#import geni.util
from time import sleep
from sys import exc_info
from traceback import print_exception

class TCPServer(SocketServer.ThreadingTCPServer):
    '''
     Multi-threaded TCP server
    '''
    allow_reuse_address = True
    print "### Starting VirtualFiber server..."
    print "    - Service alias [", SERVER_BINDING['service_alias'], "]"

class TCPRequestHandler(SocketServer.BaseRequestHandler):
    '''
     Specific JSON/TCP request handler
    '''
    def __init__(self, request, client_address, server):
        # Read configuration parameter
        self.__isdebug = CONTEXT['debug']
        self.__size = CONTEXT['request_size']
        self.__logger = get_logger("TCPRequestHandler")

        # Compression Utility
        self.__compressedcontent = CONTEXT['compressed_content']
        self.__compression = Utility()
        self.__client = client_address

        # populate the seller list
        self.__sellerObj = server.sellerObject

        # Initialize Ad Exchange
        self.__adExObject = server.adExObject

        # Initialize the DB connection
        self.__dbConnection = DBConnection()

        if DB_PARAMS['truncate']:
            self.__dbConnection.query("truncate table `VirtualFiber`.`IPAllocation`")

        self.__infra_tested = TEST_PARAMS['infra_tested']

        if self.__infra_tested == "MININET":
            self.__mininetConnection = server.mininetConnection
            self.__floodlightConnection = server.floodlightConnection

        # Call base class
        BaseRequestHandler.__init__(self, request, client_address, server)

    def getFlowTuples(self, item):
        flowTuples = []
        for ipA, ipB, portA, portB in zip(item.ipA.split(','), item.ipB.split(','), \
                                          item.portA.split(','), item.portB.split(',')):
            flowTuples.append((ipA, ipB, portA, portB))
        return flowTuples

    def handle(self):
        '''
         Service handler method
        '''
        try:
            self.__logger.debug("[TCPRequestHandler][handle]Connection accepted... processing")

            # Reading request (assuming a small amount of bytes)
            data = ""
            while True:
                new_data = self.request.recv(self.__size).strip()
                data += new_data
                if '}' in new_data: break

            # Unmarshall the request
            request = Request('', 0, '')
            self.__logger.debug("[TCPRequestHandler][handle]Received json data: %s", str(data))
            request.from_json(data)
            # Print data out, if debug

            layer3 = Layer3()

            overheadList = []
            with Timer() as tTotalProcessing:
                self.__logger.debug("[TCPRequestHandler][handle]Received data: %s", str(request.content))

                if (request.name == "BUYER" and request.code == 100):
                    self.__logger.info("Request from Buyer received.")
                    ClientRequest = collections.namedtuple('ClientRequest','linkA linkB numberOfStrands \
                                                                            capacityPerStrand bidPerStrand \
                                                                            clientName winnerFlag toPay \
                                                                            ipA ipB portA portB \
                                                                            ISP prefixA prefixB')
                    crDict = defaultdict(list)
                    # prepare requests data and store it in a namedtuple
                    for r in request.content:
                        if r.startswith("#"): continue
                        vals = r.strip().split(";")
                        va1 = vals[0].strip()
                        va2 = vals[1].strip()
                        cr = ClientRequest(linkA=va1, linkB=va2, numberOfStrands=int(vals[2]), \
                                        capacityPerStrand=int(vals[3]), bidPerStrand=int(vals[4]), \
                                        clientName=vals[5].strip(), winnerFlag=0, toPay=0, \
                                        ipA='', ipB='', portA='', portB='', \
                                        ISP='', prefixA='', prefixB='')
                        key = va1+"#"+va2
                        crDict[key].append(cr)

                    # Dispatch the request to the Adex
                    self.__logger.debug("[TCPRequestHandler][handle]Dispatching request to the Ad Exchange...")
                    with Timer() as tAd:
                        allocationList = self.__adExObject.processClientRequests(crDict, self.__sellerObj)
                    val = tAd.printTime("AdExchange", tAd, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                    overheadList.append(val)
                    # Allocate IP address for circuits
                    updatedList = layer3.allocateIPAddresses(self.__sellerObj.getSellerGraph(), allocationList, self.__dbConnection)

                    self.__logger.debug("IP address and interface allocations decisions.")
                    for u in updatedList:
                        self.__logger.debug(u)

                    # Create e-2-e path for client
                    if self.__infra_tested == 'REAL':
                        self.__logger.info("Launching real network experiments.")
                        with Timer() as tCircuitCreation:
                            for item in updatedList:
                                if item.winnerFlag == 1:
                                    # Create circuits
                                    flowTuples = self.getFlowTuples(item)

                                    # Push circuits
                                    locationA = (item.linkA.split(",")[1]).strip()
                                    locationB = (item.linkB.split(",")[1]).strip()
                                    capacity = item.capacityPerStrand
                                    with Timer() as tGeneration:
                                        switch_ips = ["192.168.57.100", "192.168.57.101"]
                                        for ip in switch_ips:
                                            addLink(ip, capacity)
                                    val = tCreation.printTime("CircuitCreation", tCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                    overheadList.append(val)
                                    self.__logger.info("Circuit pushed into networks by vFiber for winner: {0}".format(item.clientName))
                        val = tCircuitCreation.printTime("TotalGenerationAndCreation", tCircuitCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        overheadList.append(val)

                    elif self.__infra_tested == 'MOCK':
                        self.__logger.info("Launching mock network experiments.")
                        with Timer() as tCircuitCreation:
                            for item in updatedList:
                                if item.winnerFlag == 1:
                                    # Create circuits
                                    flowTuples = self.wTuples(item)

                                    # Push circuits
                                    locationA = (item.linkA.split(",")[1]).strip()
                                    locationB = (item.linkB.split(",")[1]).strip()
                                    capacity = item.capacityPerStrand
                                    with Timer() as tCreation:
                                        val = tCreation.printTime("CircuitCreation", tCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                    overheadList.append(val)

                                    self.__logger.info("Circuit pushed into networks by vFiber for winner: {0}".format(item.clientName))
                        val = tCircuitCreation.printTime("TotalGenerationAndCreation", tCircuitCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        overheadList.append(val)
                    else:
                        raise ValueError('Wrong configuration parameter in TEST_PARAMS')

                    # Prepare the response data
                    response = Data(True, [], 0)
                    response.vector = updatedList
                    response.nrbytes = int(sys.getsizeof(updatedList))

                    # Marshall JSON representation
                    json_str = response.to_json()
                    self.__logger.debug("[TCPRequestHandler][handle](Original) JSON Dimension:: %d", sys.getsizeof(json_str))
                    c_response = self.__compression.compress(json_str)
                    self.__logger.debug("[TCPRequestHandler][handle](Compressed) JSON Dimension:: %d", sys.getsizeof(c_response))
                    self.request.sendall(c_response)
                    self.__logger.debug("[TCPRequestHandler][handle]Bunch of compressed data sent back!")

                elif (request.name == "SDX" and request.code == 001):
                    self.__logger.info("Request from SDX received.")
                else:
                    self.__dbConnection.close()
                    self.__sshConnection.close()
                    raise ValueError('Bad request name and code. Either should be from SDX or from Buyer.')
            val = tTotalProcessing.printTime("ProcessClientRequest", tTotalProcessing, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
            overheadList.append(val)

            strVal = "\n".join(overheadList)
            print strVal
            # call only when a coarse grained plot is needed
            # a = StringIO(strVal)
            # plotTimeline(a, CONTEXT['meas_to_location']+"overhead.eps")

        except Exception, e:
            # self.__dbConnection.close()
            # self.__sshConnection.close()
            self.__logger.error("Exception upon message reception: %s", str(e))
            exc_type, exc_value, exc_traceback = exc_info()
            print_exception(exc_type, exc_value, exc_traceback)

        finally:
            self.__dbConnection.close()
