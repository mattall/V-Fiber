'''
Cluster_scalability_tester.py

The purpose of this script is to test the performance of vFiber for 
various cluster sizes, topologies, and link activation times.

Example: $ python Cluster_scalability_tester 3

This will run vFiber on a cluster of 3 servers, on a ciruct 
topology, using the mean activation time from benchmarking tests to 
simulate the link activation time.

results are stored in "./results/{cluster_size}_{topology}_{time}.txt
'''
#from test_startClient import start_client
from testClient import TCPClient
from multiprocessing import Process
from time import sleep, time
from server_details import SERVERS
import argparse
import paramiko
import logging
from settings import SERVER_BINDING
from random import choice
from os import listdir
from os.path import isfile, join

def (servers, path, data):
    print("Thread is initializing client")
    
    client = TCPClient(server_hosts=servers,path_to_data=path,buyer_data=data,totalReqs=1)
    start = time()
    client.start()
    client.join()
    end = time()
    print(end - start)

def do_ssh(username, address, password, server, cluster_size):
    port = 22
    paramiko.util.log_to_file("ssh.log")
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    c.exec_command("killall -9 python; cd /home/matt/vFiber/V-Fiber/src;\
                     source ../../bin/activate; \
                     python startVFCluster.py {0} {1}&>> {2}.log".\
                     format(server, cluster_size ,time()))
    c.close()

def end_a_server(username, address, password, server):
    port = 22
    paramiko.util.log_to_file("terminate_server.log")
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    stdin, stdout, stderr = c.exec_command("killall -9 python")
    c.close()

def main(args):
    server_procs = [] 

    # Start Distributed Controller ervers
    for s in SERVERS:
        if int(s) <= args.cluster_size:
            print('='*30)
            user = SERVERS[s]['user']
            addr = SERVERS[s]['address']
            pw = SERVERS[s]['password']
            p = Process(target = do_ssh, args = (user, addr, pw, s, args.cluster_size))
            p.start()
            server_procs.append(p)

    sleep(5)

    buyer_path = "/Users/TomNason/Dropbox/VFiber_code/VFiber/data/star/starBuyers/"
    buyer_files = [f for f in listdir(buyer_path) if isfile(join(buyer_path, f))]

    # Start up a client thread, and track its time-to-complete
    vF_severs = SERVER_BINDING['address'][:args.cluster_size]
    while (1):
        req_file = "/"+choice(buyer_files)
        if ".gz" not in req_file:
            break

    client_procs = []
    for r in range(args.reqs_to_send):
        p = Process(target = timed_client_thread, args = (vF_severs, buyer_path, req_file))
        p.start()
        client_procs.append(p)

    start = time()
    for p in client_procs:
        p.join()
    end = time()

    request_time = (end - start)

    # Terminate Ditributed Controller servers
    for s in SERVERS:
        if int(s) <= args.cluster_size:
            print('='*30)
            user = SERVERS[s]['user']
            addr = SERVERS[s]['address']
            pw = SERVERS[s]['password']
            end_a_server(user, addr, pw, s)
            print("vFiber shutdown on server '%s' connected at %s" % (s, addr))

    # write test to file
    test_file = "{}_{}_{}_{}.txt".format(\
                    args.cluster_size, args.topology, args.time, args.reqs_to_send)    
    with open(test_file, 'a+') as file:
        file.write("{}\n".format(request_time))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("cluster_size", type=int, help="Max Number of servers to evaluate cluster")
    parser.add_argument("topology", type=str, help="circuit, two-link, star?")
    parser.add_argument("time", type=str, help="mean, max, or min")
    parser.add_argument("reqs_to_send", type=int, help="10, 20, 100?")

    args = parser.parse_args()
    main(args)
