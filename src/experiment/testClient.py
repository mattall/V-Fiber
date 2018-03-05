import socket, time, threading, sys, gzip

from base.model.datamodel import Request, Data, Utility
from settings import CONTEXT, SERVER_BINDING, TEST_PARAMS
from threading import Thread
from common import get_logger

"""
This client differs from the core clinet in that it accepts a string parameter
called testReq which deatils the client's request
"""

class TCPClient(threading.Thread):
    '''
     JSON/TCP client thread
    '''
    def __init__(self, buyer_data = TEST_PARAMS['buyer_file_name'], testReq = None):
        '''
         Class constructor
        '''
        Thread.__init__(self)

        # Remote service bindings
        self.__serverhost = SERVER_BINDING['address']
        self.__serverport = int(SERVER_BINDING['port'])
        # Buffer settings
        self.__bufferdim = int(CONTEXT['client_socket_buffer'])
        # Compression helper
        self.__compression = Utility()
        self.__resourcepath = TEST_PARAMS['path']
        self.__buyerFile = buyer_data
        self.__client_request_type = TEST_PARAMS['client_request_type']
        self.__client_request_code = TEST_PARAMS['client_request_code']
        self.__logger = get_logger("TCPClient")

        self.testReq = testReq

    def run(self):
        '''
         Thread handler
        '''
        try:
            # Request creation
            if self.testReq:
                bidList = [self.testReq]
                testfile = None
                zippedfile = None
            else:
                resource = []
                resource.append(self.__resourcepath)
                resource.append(self.__buyerFile)
                self.__logger.debug("[TCPClient][run]Resource read: {}\n".format(resource))

                # Test if compressed content is needed
                bidList = []
                zippedfile = None
                testfile = None
                if (self.__compression):
                    zippedfile = gzip.open(''.join(resource)+".gz", "r+")
                    bidList = zippedfile.readlines()
                    self.__logger.info("[TCPClient][run](Compressed) Content size {0}".format(sys.getsizeof(bidList)))
                else:
                    testfile = open(''.join(resource), 'r')
                    bidList = testfile.readlines()
                    self.__logger.info("[TCPClient][run](Uncompressed) Content size {0}".format(sys.getsizeof(bidList)))

            data = Request(self.__client_request_type, self.__client_request_code, bidList)

            # Client socket binding
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.__serverhost, self.__serverport))

            # Sending JSON data over the socket
            sock.send(data.to_json())
            self.__logger.info("[TCPClient][run]Request sent...")
            start = time.time()
            response = self.__receive_data(sock)
            end = time.time()

            self.__logger.debug("[TCPClient][run]Reception::Time Elapsed: {0}".format(end - start))
            self.__logger.debug("[TCPClient][run](Compressed) Dimension:: {0}".format(sys.getsizeof(response)))

            # Treating compressed data
            result = self.__compression.decompress(response)
            data = Data(False, [], 0)
            data.from_json(result)
            if (int(data.nrbytes) == sys.getsizeof(data.vector)):
                self.__logger.info("[TCPClient][run]Integrity is OK")
                self.__logger.info("[TCPClient][run]Allocations")
                for allocation in data.vector:
                    self.__logger.info(allocation)

        except Exception, e:
            self.__logger.error("Error::NET::sending exception {0}".format(e))
        finally:
            if (testfile):
                testfile.close()
            if (zippedfile):
                zippedfile.close()
            sock.close()

    def __receive_data(self, client_socket):
        '''
         Helper method: buffered network reader
        '''
        self.__logger.info("[TCPClient][run]Receiving response...")
        data = ''
        while True:
            # Iteratively read the socket according to buffer size
            result = client_socket.recv(self.__bufferdim)
            if (not result):
                break
            data += result

        return data
