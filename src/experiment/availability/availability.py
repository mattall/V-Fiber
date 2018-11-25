#from test_startClient import start_client
from testClient import TCPClient
from threading import Thread, enumerate, current_thread, Lock
from multiprocessing import Process
from time import sleep, time
from numpy.random import poisson
from pandas import read_csv
from random import choice, randint, sample
from settings import SERVER_BINDING
from server_details import SERVERS
import argparse
import paramiko
import pickle as pkl
import matplotlib.pyplot as plt
import matplotlib as mpl
from numpy import median
from plot_availability_data import create_plot
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (10240, 10240))

# import logging
#
# logging.getLogger("paramiko").setLevel(logging.WARNING)

def client_thread(req, req_path = None, req_file = None):
    print("Thread is initializing client with totalReqs = {}, buyer_data = {}".format(req, req_file))
    client = TCPClient(totalReqs = req, buyer_data = req_file, path_to_data = req_path)
    client.start()
    return client

def end_two_servers(log='', start_t=0, stops=''):
    victims = sample(SERVERS.items(), 2)
    for s, target in victims:
        end_a_server(target['user'], target['address'], target['password'], s)
        elapsed_time = time_since(start_t)
        log += "vFiber shutdown on server '%s' at time %s\n" % (s, elapsed_time)
        stops.append(elapsed_time)
    return victims, log, stops

def revive_two_servers(patients, log='', start_t=0, starts=''):
    for s, target in patients:
        do_ssh(target['user'], target['address'], target['password'], s)
        elapsed_time = time_since(start_t)
        log += "vFiber started on server '%s' at time %s\n" % (s, elapsed_time)
        starts.append(elapsed_time)
    return log, starts

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

def time_since(start):
    return time() - start

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
    c.exec_command("killall -9 python; cd /home/matt/vFiber/V-Fiber/src; source ../../bin/activate; python startVFCluster.py {} &>> {}.log".format(server,time()))
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
        print "Connection to {0} closed!".format(conn)

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
    failure_testing = args.failure_testing
    use_poisson = True if args.use_poisson == 'y' else False
    wait_time = args.wait_time
    log = ''

    reqs_sent = 0 # updated throughout experiment
    server_cons = {}
    server_procs = []
    activity_log  = []

    #Connect to GC Servers
    for s in SERVERS:
        print('='*30)
        user = SERVERS[s]['user']
        addr = SERVERS[s]['address']
        pw = SERVERS[s]['password']
        p = Process(target = do_ssh, args = (user, addr, pw, s))
        p.start()
        server_procs.append(p)

    for p in server_procs:
        p.join()

    sleep(5)

    thread_reqs = [] # list of ordered-pairs, (thread, requests_in_thread)
    starts = []
    stops = []

    START_TIME = time()

    if failure_testing == '2min2takedown':         
        END_TIME = START_TIME + 120 + wait_time + 120
        services_terminated = False
        services_recovered = False

    
    else:
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

        elapsed_time = time() - START_TIME

        if failure_testing == '2min2takedown':
            if START_TIME + 120 < time():
                if not services_terminated:
                    victims, log, stops = end_two_servers(log, START_TIME, stops)
                    services_terminated = True

            if START_TIME + 120 + wait_time < time():
                if not services_recovered:
                    log, starts = revive_two_servers(victims,log, START_TIME, starts)
                    services_recovered = True

        if failure_testing == 'p':
            """
            Kill a random server every two minutes, starting at one minute.
            Bring the server back online after one minute.
            """
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

        elif failure_testing == 'd':
            if START_TIME + 60 < time() < START_TIME + 61:
                victims, log, stops = end_two_servers(log, START_TIME, stops)

            if START_TIME + 70 < time() < START_TIME + 71:
                log, starts = revive_two_servers(victims,log, START_TIME, starts)
            
            if START_TIME + 120 < time() < START_TIME + 121:
                victims, log, stops = end_two_servers(log, START_TIME, stops)

            if START_TIME + 140 < time() < START_TIME + 141:
                log, starts = revive_two_servers(victims,log, START_TIME, starts)

            if START_TIME + 180 < time() < START_TIME + 181:
                victims, log, stops = end_two_servers(log, START_TIME, stops)

            if START_TIME + 210 < time() < START_TIME + 211:
                log, starts = revive_two_servers(victims,log, START_TIME, starts)

            if START_TIME + 300 < time() < START_TIME + 301:
                victims, log, stops = end_two_servers(log, START_TIME, stops)
            
            if START_TIME + 360 < time() < START_TIME + 361:
                log, starts = revive_two_servers(victims,log, START_TIME, starts)

            # Artifact code from old dead-stop failure test.
            # if START_TIME + 60 < time() < START_TIME + 61:
            #     target = SERVERS['1']
            #     end_a_server(target['user'], target['address'], target['password'], '1')
            #     log += "vFiber shutdown on server '%s' at time %s\n" % ('1', elapsed_time)
            #     stops.append(elapsed_time)

            # if START_TIME + 120 < time() < START_TIME + 121:
            #     target = SERVERS['2']
            #     end_a_server(target['user'], target['address'], target['password'], '2')
            #     log += "vFiber shutdown on server '%s' at time %s\n" % ('2', elapsed_time)
            #     stops.append(elapsed_time)

            # if START_TIME + 150 < time() < START_TIME + 151:
            #     target = SERVERS['1']
            #     do_ssh(target['user'], target['address'], target['password'], '1')
            #     log += "vFiber started on server '%s' at time %s\n" % ('1', elapsed_time)
            #     starts.append(elapsed_time)

            # if START_TIME + 200 < time() < START_TIME + 201:
            #     target = SERVERS['2']
            #     do_ssh(target['user'], target['address'], target['password'], '2')
            #     log += "vFiber started on server '%s' at time %s\n" % ('2', elapsed_time)
            #     starts.append(elapsed_time)

            # if START_TIME + 420 < time() < START_TIME + 421:
            #     target = SERVERS['2']
            #     end_a_server(target['user'], target['address'], target['password'], '2')
            #     log += "vFiber shutdown on server '%s' at time %s\n" % (2, elapsed_time)
            #     stops.append(elapsed_time)

            #     target = SERVERS['3']
            #     end_a_server(target['user'], target['address'], target['password'], '3')
            #     log += "vFiber shutdown on server '%s' at time %s\n" % ('3', elapsed_time)
            #     stops.append(elapsed_time)

            # if START_TIME + 450 < time() < START_TIME + 451:
            #     target = SERVERS['2']
            #     do_ssh(target['user'], target['address'], target['password'], '2')
            #     log += "vFiber started on server '%s' at time %s\n" % ('2', elapsed_time)
            #     starts.append(elapsed_time)

        sleep(DELTA)

    while threads_working and (time() < END_TIME + 15):
        print("[experiment][main]Late birds finishing up in (t - {0})".format(int(END_TIME + 10 - time())))
        threads_working = update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME)
        sleep(1)

    #update_activity_log(activity_log, thread_reqs, reqs_sent, START_TIME)

    for s in SERVERS:
        print('='*30)
        user = SERVERS[s]['user']
        addr = SERVERS[s]['address']
        pw = SERVERS[s]['password']
        end_a_server(user, addr, pw, s)
        print("vFiber shutdown on server '%s' connected at %s" % (s, addr))

    #sanity check -- reqs in thread reqs is same as reqs_sent
    print('*'*30)
    print 'number of requests sent {}'.format(reqs_sent)
    print 'requests over time\n{}'.format(activity_log)
    print log
    print("stops:", stops)
    print("starts:", starts)

    # write test to file
    if wait_time:
        test_file = "availability_experiment_length-{}:delta-{}:volume-{}:failure_testing-{}:wait_time-{}:poisson-{}.pkl".format(TEST_DURRATION,DELTA,REQUESTS_PER_TIC,failure_testing,wait_time,use_poisson)
    else:
        test_file = "availability_experiment_length-{}:delta-{}:volume-{}:failure_testing-{}:poisson-{}.pkl".format(TEST_DURRATION,DELTA,REQUESTS_PER_TIC,failure_testing,use_poisson)
    
    with open(test_file, 'w') as file:
        pkl.dump(activity_log, file)

    create_plot(test_file, 5, starts, stops)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--length", help="Number of seconds to run experiment.", dest="length", default=2, type=int)
    parser.add_argument("-d", "--delta", help="Number of seconds between batch sending.", dest="delta", default=1, type=int)
    parser.add_argument("-v", "--volume", help="Rough number of requests to send per time delta.", dest="volume", default=10, type=int)
    parser.add_argument("-p", "--use_poisson", help="True or False, identify wheather to use Poisson for generating requests", dest="use_poisson", type=str)
    parser.add_argument("-f", "--filename", help="Name of file where request data resides.")
    parser.add_argument("-t", "--failure_testing", help="p for periodic, d for deadstop, or n for no", dest="failure_testing", default=False, type=str)
    parser.add_argument("-w", "--wait_time", help="for 2min takedown experiment, specify down time in seconds.", dest="wait_time", type=int, default=None)

    args = parser.parse_args()
    main(args)
