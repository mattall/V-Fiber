#from test_startClient import start_client
from testClient import TCPClient
from threading import Thread, enumerate, current_thread
from time import sleep, time
from numpy.random import poisson
from pandas import read_csv
from random import choice, randint
from client_settings import SERVER_BINDING

def client_thread(req):
    print("Thread is initializing client")
    client = TCPClient(testReq = req)
    client.start()
    return client

# def get_leader():
#     "send a request to learn the leader's IP."
#     connected = False
#     hosts = SERVER_BINDING['address']
#     while not connected and hosts:
#         host = hosts.pop();
#         try:
#             self.__logger.debug("[TCPClient][run]Trying to connect to host {0}".format(host))
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.settimeout(self.__conn_timeout)
#             sock.connect((host, self.__serverport))
#             print(connected)
#             connected = True
#             sock.settimeout(self.__recv_timeout)
#         except socket.error as e:
#             self.__logger.debug("[TCPClient][run]Failed to connect to host {0}".format(host))
#             if not hosts:
#                 self.__logger.error("Error::NET::No hosts available")
#                 raise Exception
#         try:
#             sock.send("leader")
#             leader = sock.recv(1024)

def gen_request():
    '''
    This function reads data from the sellerData.txt file and generates requests
    for resources in that file.
    '''
    sellers = read_csv("/Users/TomNason/Dropbox/VFiber_code/VFiber/data/sellerData.txt", sep=';')
    sources = sellers['#LinkA']
    destinations = sellers['LinkB']
    #
    source = choice(sources)
    dest = choice(destinations)
    while dest.strip() == source.strip():
        dest = choice(destinations)

    strands = randint(1, 2)
    capacity = randint(1, 100)
    bid = randint(600, 1000)
    #
    request = "{:27};{:27};{:13};{:8};{:5};{:6}\n".format(source, dest, strands, capacity, bid, 0)
    return request

TEST_DURRATION = 1   # senconds
DELTA = 1 # number of seconds between requests
REQUESTS_PER_TIC = 10

reqs_sent = 0 # updated throughout experiment
active_log = []

START_TIME = time()
END_TIME = START_TIME + TEST_DURRATION
while time() < END_TIME:
    print('time till finished is {}'.format(END_TIME - time()))
    req_count = poisson(REQUESTS_PER_TIC)
    for i in range(req_count):
        req = gen_request()
        print("dispatching request to client: {}".format(req))
        t = client_thread(req)
        reqs_sent += 1

    sleep(DELTA)
    # add number of currently running threads to active_log
    elapsed_time = time() - START_TIME
    active_reqs = len(enumerate()) - 1 # main is not a client thread
    completed_threads = reqs_sent - active_reqs
    active_log.append( (elapsed_time, completed_threads/elapsed_time) )

for t in enumerate():
    if t != current_thread():
        t.join()

active_reqs = len(enumerate()) - 1 # main is not a client thread
completed_threads = reqs_sent - active_reqs
active_log.append( (elapsed_time, completed_threads/elapsed_time) )

print('*'*30)
print 'number of requests sent{}'.format(reqs_sent)
print 'requests over time\n{}'.format(active_log)
