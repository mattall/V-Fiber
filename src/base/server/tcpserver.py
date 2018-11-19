import SocketServer, time, gzip, sys, collections
from SocketServer import BaseRequestHandler
from base.model.datamodel import Request, Data, Utility
from adexchange.adexchange import AdExchange
from adexchange.seller import Seller
from adexchange.dbConnection import DBConnection
from settings import CONTEXT, SERVER_BINDING, DB_PARAMS, TEST_PARAMS
from collections import defaultdict, namedtuple
from common import get_logger, Timer
from realdeployment.lab_testbed import addLink
from realdeployment.torchbearer import light_path, extinguish_path
from realdeployment.ExperimentOverhead.plotTimeline import *
from subprocess import call
from StringIO import StringIO
from time import sleep
from sys import exc_info
from traceback import print_exception
from time import time
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
            request.from_json(data)

            overheadList = []
            with Timer() as tTotalProcessing:
                self.__logger.debug("[TCPRequestHandler][handle]Received data: %s", str(request.content))

                if (request.name == "BUYER" and request.code == 100):
                    self.__logger.info("Request from Buyer received.")
                    ClientRequest = namedtuple('ClientRequest','linkA linkB numberOfStrands \
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
                    self.__logger.debug("[TCPRequestHandler][handle]Dispatching request to the Fiber Exchange...")
                    with Timer() as tAd:
                        allocationList, ip_port_pairs = self.__adExObject.processClientRequests(crDict, self.__sellerObj)
                    val = tAd.printTime("FiberExchange", tAd, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                    self.__logger.info("[TCPRequestHandler][handle]Exchange Time {}".format(val))
                    overheadList.append(val)
                    self.__logger.debug("[TCPRequestHandler][handle]Received allocation List from Fiber Exchange...{}".format(allocationList))
                    self.__logger.debug("[TCPRequestHandler][handle]Received ip_port_pairs from Fiber Exchange...{}".format(ip_port_pairs))
                    # Allocate IP address for circuits
                    # allocationList = layer3.allocateIPAddresses(self.__sellerObj.getSellerGraph(), allocationList, self.__dbConnection)

                    self.__logger.debug("[TCPRequestHandler][handle]IP address and interface allocations decisions.")
                    for u in allocationList:
                        self.__logger.debug("[TCPRequestHandler][handle] {}".format(u))

                    # Create e-2-e path for client
                    if self.__infra_tested == 'REAL':
                        self.__logger.info("Launching real network experiments.")
                        with Timer() as tCircuitCreation:
                            for item in allocationList:
                                if item.winnerFlag == 1:
                                    # Create circuits
                                    with Timer() as tGeneration:
                                        flowTuples = self.getFlowTuples(item)

                                        # Push circuits
                                        self.__logger.info("Launching real network experiments. connecting {} and {}".format(item.linkA, item.linkB))
                                        if "," in item.linkA:
                                            locationA = (item.linkA.split(",")[1]).strip()
                                        else:
                                            locationA = item.linkA[1].strip()
                                        if "," in item.linkB:
                                            locationB = (item.linkB.split(",")[1]).strip()
                                        else:
                                            locationB = item.linkB[1].strip()
                                        capacity = item.capacityPerStrand

                                        # switch_ips = ["192.168.57.200", "192.168.57.201"]
                                    val = tGeneration.printTime("Configuration Generation", tGeneration, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                    with Timer() as tCreation:
                                        light_path(ip_port_pairs)
                                    val = tCreation.printTime("CircuitCreation", tCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                    self.__logger.info("[TCPRequestHandler][handle]Creation Time {}".format(val))
                                    overheadList.append(val)
                                    self.__logger.info("Circuit pushed into networks by vFiber for winner: {0}".format(item.clientName))
                        val = tCircuitCreation.printTime("TotalGenerationAndCreation", tCircuitCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        self.__logger.info("[TCPRequestHandler][handle]Generation and Creation Time {}".format(val))
                        overheadList.append(val)

                    elif self.__infra_tested == 'MOCK':
                        self.__logger.info("Launching mock network experiments.")
                        with Timer() as tCircuitCreation:
                            for item in allocationList:
                                if item.winnerFlag == 1:
                                    for ip, port in ip_port_pairs:
                                        self.__logger.debug("Pushing circuit to {} interface {} * PENDING **".format(ip, port))
                                        sleep(TEST_PARAMS['install_time']/2)
                                        self.__logger.debug("Circuite Pushed to {} interface {} *** OKAY ***".format(ip, port))
                                    
                                    capacity = item.capacityPerStrand
                                    self.__logger.info("Circuit pushed into networks by vFiber for winner: {0}".format(item.clientName))
                        val = tCircuitCreation.printTime("TotalCreationTime", tCircuitCreation, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        self.__logger.info("[TCPRequestHandler][handle]Creation Time {}".format(val))
                        overheadList.append(val)
                    else:
                        raise ValueError('Wrong configuration parameter in TEST_PARAMS')

                    # Prepare the response data
                    response = Data(True, [], 0)
                    response.vector = allocationList
                    response.nrbytes = int(sys.getsizeof(allocationList))

                    # Marshall JSON representation
                    json_str = response.to_json()
                    self.__logger.debug("[TCPRequestHandler][handle](Original) JSON Dimension:: %d", sys.getsizeof(json_str))
                    c_response = self.__compression.compress(json_str)
                    self.__logger.debug("[TCPRequestHandler][handle](Compressed) JSON Dimension:: %d", sys.getsizeof(c_response))
                    self.request.sendall(c_response)
                    self.__logger.debug("[TCPRequestHandler][handle]Bunch of compressed data sent back!")

                elif (request.name == "BUYER" and request.code == 101):
                    self.__logger.info("Request to terminate buyer's allocation.")
                    ClientRequest = namedtuple('ClientRequest','linkA linkB numberOfStrands \
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

                    # get interfaces from seller graph
                    self.__logger.debug("[TCPRequestHandler][handle]Dispatching request to the Fiber Exchange...")
                    with Timer() as tAd:
                        allocationList, ip_port_pairs = self.__adExObject.returnAllocationToInfrustructureGraph(crDict, self.__sellerObj)
                    val = tAd.printTime("returnAllocation", tAd, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                    self.__logger.info("[TCPRequestHandler][handle]Exchange Time {}".format(val))
                    overheadList.append(val)

                    # take back the e-2-e path
                    if self.__infra_tested == 'REAL':
                        self.__logger.info("[TCPRequestHandler][handle]Launching real network experiments.")
                        with Timer() as tCircuitConfigDestruction:
                            for item in allocationList:
                                # Create circuits
                                with Timer() as tGeneration:
                                    flowTuples = self.getFlowTuples(item)

                                    # Push circuits
                                    self.__logger.info("[TCPRequestHandler][handle]Disconnecting {} and {}".format(item.linkA, item.linkB))
                                    if "," in item.linkA:
                                        locationA = (item.linkA.split(",")[1]).strip()
                                    else:
                                        locationA = item.linkA[1].strip()
                                    if "," in item.linkB:
                                        locationB = (item.linkB.split(",")[1]).strip()
                                    else:
                                        locationB = item.linkB[1].strip()
                                    capacity = item.capacityPerStrand

                                    # switch_ips = ["192.168.57.200", "192.168.57.201"]
                                val = tGeneration.printTime("Configuration Generation", tGeneration, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                with Timer() as tDestruction:
                                    extinguish_path(ip_port_pairs)
                                val = tDestruction.printTime("CircuitDestruction", tDestruction, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                self.__logger.info("[TCPRequestHandler][handle]Circuit Destruction Time {}".format(val))
                                overheadList.append(val)
                                self.__logger.info("Circuit pulled from networks by vFiber from client: {0}".format(item.clientName))
                        val = tCircuitConfigDestruction.printTime("TotalGenerationAndDestruction", tCircuitConfigDestruction, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        self.__logger.info("[TCPRequestHandler][handle]Configuration Generation and Circuit Destruction Time {}".format(val))
                        overheadList.append(val)

                    elif self.__infra_tested == 'MOCK':
                        self.__logger.info("[TCPRequestHandler][handle]Launching real network experiments.")
                        with Timer() as tCircuitConfigDestruction:
                            for item in allocationList:
                                # Create circuits
                                with Timer() as tGeneration:
                                    flowTuples = self.getFlowTuples(item)

                                    # Push circuits
                                    self.__logger.info("[TCPRequestHandler][handle]Disconnecting {} and {}".format(item.linkA, item.linkB))
                                    if "," in item.linkA:
                                        locationA = (item.linkA.split(",")[1]).strip()
                                    else:
                                        locationA = item.linkA[1].strip()
                                    if "," in item.linkB:
                                        locationB = (item.linkB.split(",")[1]).strip()
                                    else:
                                        locationB = item.linkB[1].strip()
                                    capacity = item.capacityPerStrand

                                    # switch_ips = ["192.168.57.200", "192.168.57.201"]
                                val = tGeneration.printTime("Configuration Generation", tGeneration, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                with Timer() as tDestruction:
                                    sleep(0.001)
                                val = tDestruction.printTime("CircuitDestruction", tDestruction, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                                self.__logger.info("[TCPRequestHandler][handle]Circuit Destruction Time {}".format(val))
                                overheadList.append(val)
                                self.__logger.info("Circuit pulled from networks by vFiber from client: {0}".format(item.clientName))
                        val = tCircuitConfigDestruction.printTime("TotalGenerationAndDestruction", tCircuitConfigDestruction, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
                        self.__logger.info("[TCPRequestHandler][handle]Configuration Generation and Circuit Destruction Time {}".format(val))
                        overheadList.append(val)                    else:
                        raise ValueError('Wrong configuration parameter in TEST_PARAMS')

                elif (request.name == "MONITOR" and request.code == 102):
                    self.__logger.info("[TCPRequestHandler][handle]Request from Monitor received.")
                    (ip, port) = request.content 
                    self.__logger.debug("[TCPRequestHandler][handle]Broken Link: {}".format(ip, port))
                    try:
                        (x, y, port_pair) = self.__sellerObj.find_edge_from_ip_port_pair((ip, port))                        
                        harzardous_path = self.__sellerObj.update_disconnected_strand(x, y, port_pair)
                        new_path = self.__sellerObj.aquire_strand(x, y, 0)
                        self.__logger.info("[TCPRequestHandler][handle]Cleaning up bad path.")
                        extinguish_path(harzardous_path)
                        self.__logger.info("[TCPRequestHandler][handle]Allocating new path.")
                        light_path(new_path)
                    except TypeError:
                        pass


                elif (request.name == "SDX" and request.code == 001):
                    self.__logger.info("Request from SDX received.")

                else:
                    self.__dbConnection.close()
                    raise ValueError('Bad request name and code. Either should be from SDX or from Buyer.')
            
            val = tTotalProcessing.printTime("ProcessClientRequest", tTotalProcessing, CONTEXT['meas_format'], CONTEXT['meas_to_file'])
            self.__logger.info("[TCPRequestHandler][handle]Total Request Handling Time {}".format(val))
            overheadList.append(val)

            strVal = "".join(overheadList)
            self.__logger.debug("[TCPRequestHandler][handle] Overhead list :\n {}".format(strVal))
            # a = StringIO(strVal)
            # plotTimeline(a, CONTEXT['meas_to_location']+"overhead.eps")
            with open("./"+str(time())+"overhead.txt", "a") as file:
                file.write(strVal)
                file.close()

        except Exception, e:
            self.__logger.error("Exception upon message reception: %s", str(e))
            exc_type, exc_value, exc_traceback = exc_info()
            print_exception(exc_type, exc_value, exc_traceback)

        finally:
            self.__dbConnection.close()
