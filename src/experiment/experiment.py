#from test_startClient import start_client
from testClient import TCPClient
from threading import Thread, enumerate
from time import sleep, time
from numpy.random import poisson
from pandas import read_csv
from random import choice, randint

def client_thread():
    client = TCPClient()
    client.start()
    return client

def client_thread_t(req):
    print("Thread is initializing client")
    client = TCPClient(testReq = req)
    client.start()
    return client

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
    #
    strands = randint(1, 10)
    capacity = randint(1, 100)
    bid = randint(600, 1000)
    #
    request = "{:27};{:27};{:13};{:8};{:5};{:6}\n".format(source, dest, strands, capacity, bid, 0)
    return request

TEST_DURRATION = 60 # senconds
DELTA = 1 # number of seconds between requests
START_TIME = time()

print('starting test')


threads = []
active_log = []

END_TIME = START_TIME + TEST_DURRATION
while time() < END_TIME:
    print('time till finished is {}'.format(END_TIME - time()))
    req_count = poisson(3)
    for i in range(req_count):
        print("creating request thread")
        req = gen_request()
        print(req)
        t = client_thread_t(req)
        threads.append(t)
    # add number of currently running threads to active_log
    sleep(DELTA)
    elapsed_time = time() - START_TIME
    active_log.append( (elapsed_time, len(enumerate())) )

for t in threads:
    t.join()

print('*'*30)
print 'number of requests sent{}'.format(len(threads))
print 'requests over time\n{}'.format(active_log)
