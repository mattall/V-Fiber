#from test_startClient import start_client
from testClient import TCPClient
from threading import Thread, enumerate, current_thread, Lock
from multiprocessing import Process
from time import sleep, time
from numpy.random import poisson
from pandas import read_csv
from random import choice, randint
from settings import SERVER_BINDING
from server_details import SERVERS
import argparse
import paramiko
import pickle as pkl
import matplotlib.pyplot as plt
import matplotlib as mpl
from numpy import median

# import logging
#
# logging.getLogger("paramiko").setLevel(logging.WARNING)

def client_thread(req, req_path = None, req_file = None):
    print("Thread is initializing client with totalReqs = {}, buyer_data = {}".format(req, req_file))
    client = TCPClient(totalReqs = req, buyer_data = req_file, path_to_data = req_path)
    client.start()
    return client

# def update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME):
#     completed_threads = get_inactive_reqs(thread_reqs)
#     if activity_log:
#         previously_completed_threads = activity_log[-1][1]
#         newly_completed_threads = completed_threads - activity_log[-1][1]
#     else:
#         newly_completed_threads = completed_threads
#
#     elapsed_time = time() - START_TIME
#     activity_log.append( (elapsed_time, newly_completed_threads) )
#     if completed_threads != reqs_sent:
#         still_working = True
#     else:
#         still_working = False
#     return still_working


def update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME):
    completed_threads = get_inactive_reqs(thread_reqs)

    elapsed_time = time() - START_TIME
    activity_log.append( (elapsed_time, completed_threads) )
    if completed_threads != reqs_sent:
        still_working = True
    else:
        still_working = False
    return still_working

def get_inactive_reqs(thread_reqs):
    finished_reqs = 0
    for thread, requests_in_thread in thread_reqs:
        if not thread.isAlive():
            finished_reqs += requests_in_thread
    return finished_reqs



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

def do_ssh(username, address, password, server):
    port = 22
    paramiko.util.log_to_file("ssh.log")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    c.exec_command("killall -9 python; cd /home/matt/vFiber/V-Fiber/src; source ../../bin/activate; python startVFCluster.py %s" % server)
    c.close()

def end_a_server(username, address, password, server):
    port = 22
    paramiko.util.log_to_file("terminate_server.log")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    stdin, stdout, stderr = c.exec_command("killall -9 python")
    c.close()

def closeConnections(connections):
    for conn in connections.items():
        conn.close()
        print "Connection to {0} closed!".format(node)

def start_vFiber(server_cons, server):
    stdin, stdout, stderr = server_cons[server].exec_command("killall -9 python; cd /home/matt/vFiber/V-Fiber/src; source ../../bin/activate; python startVFCluster.py %s" % server)

def end_vFiber(server_cons, server):
    for server, conn in server_cons:
        stdin, stdout, stderr = server_cons[server].exec_command("killall -9 python")

def main(args):
    TEST_DURRATION = args.length    # senconds
    DELTA = args.delta              # number of seconds between requests
    REQUESTS_PER_TIC = args.volume
    REQ_PATH = "/Users/TomNason/Dropbox/VFiber_code/VFiber/data/"
    REQ_FILE = "clientRequest.txt"
    failure_testing = True if args.failure_testing == 'y' else False
    use_poisson = True if args.use_poisson == 'y' else False
    log = ''

    reqs_sent = 0 # updated throughout experiment
    server_cons = {}
    server_procs = []
    activity_log  = []

    # #Connect to GC Servers
    # for s in SERVERS:
    #     print('='*30)
    #     user = SERVERS[s]['user']
    #     addr = SERVERS[s]['address']
    #     pw = SERVERS[s]['password']
    #     p = Process(target = do_ssh, args = (user, addr, pw, s))
    #     p.start()
    #     server_procs.append(p)
    #
    # for p in server_procs:
    #     p.join()
    #
    # sleep(5)

    thread_reqs = [] # list of ordered-pairs, (thread, requests_in_thread)
    starts = []
    stops = []

    START_TIME = time()
    END_TIME = START_TIME + TEST_DURRATION
    s = 0
    target = None
    while time() < END_TIME:
        print("[experiment][main]Time left {0}".format(int(END_TIME - time())))
        if use_poisson:
            req_count = poisson(REQUESTS_PER_TIC)
        else:
            req_count = REQUESTS_PER_TIC
        print("[experiment][main]Requests sent {0}".format(req_count))

        t = client_thread(req_count, REQ_PATH, REQ_FILE)
        thread_reqs.append((t, req_count))
        reqs_sent += req_count
        threads_working = update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME)

        if failure_testing:
            """
            Kill a random server every two minutes, starting at one minute.
            Bring the server back online after one minute.
            """
            elapsed_time = time() - START_TIME
            if 60 < elapsed_time < 61:
                s, target = choice(SERVERS.items())
                end_a_server(target['user'], target['address'], target['password'], s)
                log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
                stops.append(elapsed_time)

            if 120 < elapsed_time < 121:
                do_ssh(target['user'], target['address'], target['password'], s)
                log += "vFiber started on server '%s' at time %s\n" % (s, elapsed_time)
                starts.append(elapsed_time)

            if 180 < elapsed_time < 181:
                s, target = choice(SERVERS.items())
                end_a_server(target['user'], target['address'], target['password'], s)
                log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
                stops.append(elapsed_time)

            if 240 < elapsed_time < 241:
                do_ssh(target['user'], target['address'], target['password'], s)
                log += "vFiber started on server '%s' at time %s\n" % (s, elapsed_time)
                starts.append(elapsed_time)

            if 300 < elapsed_time < 301:
                s, target = choice(SERVERS.items())
                end_a_server(target['user'], target['address'], target['password'], s)
                log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
                stops.append(elapsed_time)

            if 360 < elapsed_time < 361:
                do_ssh(target['user'], target['address'], target['password'], s)
                log += "vFiber started on server '%s' at time %s\n" % (s, elapsed_time)
                starts.append(elapsed_time)

            if 420 < elapsed_time < 421:
                s, target = choice(SERVERS.items())
                end_a_server(target['user'], target['address'], target['password'], s)
                log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
                stops.append(elapsed_time)

            if 480 < elapsed_time < 481:
                do_ssh(target['user'], target['address'], target['password'], s)
                log += "vFiber started on server '%s' at time %s\n" % (s, elapsed_time)
                starts.append(elapsed_time)

            if 540 < elapsed_time < 541:
                s, target = choice(SERVERS.items())
                end_a_server(target['user'], target['address'], target['password'], s)
                log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
                stops.append(elapsed_time)

        sleep(DELTA)

    while threads_working and (time() < END_TIME + 10):
        print("[experiment][main]Late birds finishing up in (t - {0})".format(int(END_TIME + 10 - time())))
        threads_working = update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME)
        sleep(1)

    #update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME)

    #sanity check -- reqs in thread reqs is same as reqs_sent
    print('*'*30)
    print 'number of requests sent {}'.format(reqs_sent)
    print 'requests over time\n{}'.format(activity_log)
    print log

    # for s in SERVERS:
    #     print('='*30)
    #     user = SERVERS[s]['user']
    #     addr = SERVERS[s]['address']
    #     pw = SERVERS[s]['password']
    #     end_a_server(user, addr, pw, s)
    #     print("vFiber shutdown on server '%s' connected at %s" % (s, addr))

    # write test to file
    test_file = "availability_experiment_length-{}:delta-{}:volume-{}:failure_testing-{}:poisson-{}.pkl".format(TEST_DURRATION,DELTA,REQUESTS_PER_TIC,failure_testing,use_poisson)
    with open(test_file, 'w') as file:
        pkl.dump(activity_log, file)

    time_t = []
    completed = []
    for x in range(1, len(activity_log)):
        # time is the first entry of the x'th tuple
        time_t.append(activity_log[x][0])
        # completed at time_t is the second entry of the x'th tuple
        # minus the second entry of the (x-1)'th tuple
        completed.append(activity_log[x][1]-activity_log[x-1][1])

    mpl.rcParams.update({'font.size': 50})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"

    label_size = 50

    axes = plt.gca()
    axes.set_ylim([-5,median(completed)*2])
    axes.set_xlim([0,time_t[-1]])
    axes.tick_params(length=16, width=4)
    lw = 3
    for s in starts:
        plt.axvline(x=s, color = 'green', linewidth=lw)

    for s in stops:
        plt.axvline(x=s, color = 'red', linewidth=lw)

    plt.gcf().subplots_adjust(bottom = 0.18, left = 0.18)
    plt.xlabel('Time (seconds)', fontsize = label_size)
    plt.ylabel('Completed Requets\n per Second', fontsize = label_size)

    plt.plot(time_t, completed)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--length", help="Number of seconds to run experiment.", dest="length", default=2, type=int)
    parser.add_argument("-d", "--delta", help="Number of seconds between batch sending.", dest="delta", default=1, type=int)
    parser.add_argument("-v", "--volume", help="Rough number of requests to send per time delta.", dest="volume", default=10, type=int)
    parser.add_argument("-p", "--use_poisson", help="True or False, identify wheather to use Poisson for generating requests", dest="use_poisson", type=str)
    parser.add_argument("-f", "--filename", help="Name of file where request data resides.")
    parser.add_argument("-t", "--failure_testing", help="y of n", dest="failure_testing", default=False, type=str)

    args = parser.parse_args()
    main(args)
