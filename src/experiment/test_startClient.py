import sys
from testClient import TCPClient

def start_client(request):
    # check for request file spec
    client = TCPClient(testReq = request)

    client.start()
    # Wait until the end of processing
    client.join()
