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

def timed_client_thread(req, req_path = None, req_file = None):
    print("Thread is initializing client with totalReqs = {}, buyer_data = {}".format(req, req_file))
    client = TCPClient(totalReqs = req, buyer_data = req_file, path_to_data = req_path)
    start = time()
    client.start()
    client.join()
    end = time()
    return (end - start)

def do_ssh(username, address, password, server):
    port = 22
    paramiko.util.log_to_file("ssh.log")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    c.exec_command("killall -9 python; a; python startVFCluster.py {} &>> {}.log".format(server,time()))
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

def main(args):
    server_procs = []
    activity_log  = []

    #Connect to GC Servers
    for s in SERVERS:
        if int(s) <= args.cluster_size:
            print('='*30)
            user = SERVERS[s]['user']
            addr = SERVERS[s]['address']
            pw = SERVERS[s]['password']
            p = Process(target = do_ssh, args = (user, addr, pw, s))
            p.start()
            server_procs.append(p)

    # for p in server_procs:
    #     p.join()

    sleep(5)

    thread_reqs = [] # list of ordered-pairs, (thread, requests_in_thread)
    starts = []
    stops = []

    # start up a a client thread, and track its time to complete

    request_time = timed_client_thread()
    print("Client Request completed in {} seconds", request_time)

    for s in SERVERS:
        if int(s) <= args.cluster_size:
            print('='*30)
            user = SERVERS[s]['user']
            addr = SERVERS[s]['address']
            pw = SERVERS[s]['password']
            end_a_server(user, addr, pw, s)
            print("vFiber shutdown on server '%s' connected at %s" % (s, addr))
    
    # write test to file
    test_file = "{}_{}_{}.txt".format(args.cluster_size, args.topology, args.time)    
    with open(test_file, 'w') as file:
        file.write(request_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-s", "--cluster_size", help = "Max Number of servers to evaluate cluster")
    parser.add_argument("-T", "--topology", help = "circuit, two-link, star?")
    parser.add_argument("-t", "--time", help="mean, max, or min")

    args = parser.parse_args()
    main(args)
