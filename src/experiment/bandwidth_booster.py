'''

This experiment demonstrates bandwidth scaling between two network end points.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                            Description
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
The network has a dumbbell topology. On one side sits a host computer running
a three virtual machines. The VMs form the vFiber Global Controller.

At the other end of the topology sits three VMs on a desktop computer. These VMs
each host iperf3 servers.

Between the two hosts is a strand of dark-fiber capable of hosting four
wavelengths through wavelength division multiplexing (WDM).

The VMs which host vFiber also host iperf3 clients. Each client sends UDP
packets to a distinct iperf3 server.

Initially there is no network connection from the iperf3 clients to the servers.
A request is sent to vFiber to 'light a path' from one end of the network to the
other. Then another request is sent to activate a new lambda every sixty
seconds.

The experiement ends 60 seconds after the last lambda is activated.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                            Analysis
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Data from each iperf3 process is dumped to the home directory of the VM it
resieds on.

After the experiment is run the files are all collected, and the throughput
observered from each process should be plotted with matplotlib.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        Network Topology Graph
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

vFiber Server 1                                                                                                                                         iperf3 Server
192.168.57.102  --\                                                           Lambda 1                                                              /-- 192.168.57.11
iperf3 Cleint      \                                                        /~~~~~~~~~~~~\                                                         /
                    \                                                      /  Lambda 2    \                                                       /
vFiber Server 2      \     192.168.57.8         192.168.57.200            /~~~~~~~~~~~~~~~~\              192.168.57.201       192.168.57.111    /      iperf3 Server
192.168.57.103  ------}--{ Host Computer }----{   Switch 1    }--{ WDM }-{    Lambda 3      }--{ WDM }--{   Switch 2    }----{ Host Computer }--{------ 192.168.57.35
iperf3 Client        /                                                    \~~~~~~~~~~~~~~~~/                                                     \
                    /                                                      \  Lambda 4    /                                                       \
vFiber Server 3    /                                                        \~~~~~~~~~~~~/                                                         \    iperf3 Server
192.168.57.104  --/                                                                                                                                 \-- 192.168.57.55
iperf3 Client

'''


#from test_startClient import start_client
from testClient import TCPClient
from threading import Thread, enumerate, current_thread, Lock
from multiprocessing import Process
from time import sleep, time
from numpy.random import poisson
from pandas import read_csv
from random import choice, randint
from settings import SERVER_BINDING
from server_details import SERVERS, PERF_SERVERS, PERF_CLIENTS
import argparse
import paramiko
from paramiko_expect import SSHClientInteraction
from torchbearer import extinguish_path as ep
from torchbearer import light_path as lp
import pexpect
import sys
from matplotlib import pyplot as plt
import matplotlib as mpl
from datetime import datetime as dt

def client_thread(req=None):
    print("Thread is initializing client")
    if req:
        client = TCPClient(totalReqs = req)
    else:
        client = TCPClient()
    client.start()
    return client

def do_ssh(username, address, password):
    port = 22
    paramiko.util.log_to_file("ssh.log")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = address, username = 'matt', password = 'root')
    c.exec_command("killall -9 python; cd /home/matt/vFiber/V-Fiber/src; source ../../bin/activate; python startVFCluster.py %s" % server)
    c.close()

def start_perf_client(server_addr, self_addr, durration):
    port = 22
    paramiko.util.log_to_file("ssh.log")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = self_addr, username = 'matt', password = 'root')
    command_str = "iperf3 -c {0} -t {1} > ./{3}_perf_client_{2}.txt".format(server_addr, durration, self_addr, dt.now().isoformat())
    command_timeout = 2*durration
    print(command_str)
    try:
        sin, sout, serr = c.exec_command(command_str, timeout = command_timeout)
        exit_status = sout.channel.recv_exit_status()          # Blocking call
        print("#"*32)
    except:
        print(serr)
    c.close()

    # data = sout
    #
    # # dump raw data to file
    # with open("bandwidth_output_{}.txt".format(self_addr), "w") as fob:
    #     fob.write(data)
    #
    # # clean up data for plotting
    # interval = []
    # transfer = []
    # bandwidth = []
    #
    # data_lines = data.split('\n')
    # for line in data_lines:
    #     if "MBytes" in line:
    #         data_point = line.split()
    #         interval.append(data_point[2].split('-')[-1])
    #         interval_unit = data_point[3]
    #         transfer.append(data_point[4])
    #         transfer_unit = data_point[5]
    #         bandwidth.append(data_point[6])
    #         bandwidth_unit = data_point[7]
    #
    # with open("bandwidth_data_output_{}.txt".format(self_addr), "w") as fob:
    #     fob.write(str(bandwidth))
    #
    # with open("bandwidth_transfer_output_{}.txt".format(self_addr), "w") as fob:
    #     fob.write(str(transfer))
    #
    # plt.subplot(2,1,1)
    # plt.plot(interval, bandwidth)
    # plt.ylabel(bandwidth_unit)
    # plt.subplot(2,1,2)
    # plt.plot(interval, transfer)
    # plt.ylabel(transfer_unit)
    # plt.xlabel(interval_unit)
    # plt.savefig("bandwidth_output_{}.png".format(self_addr.split('.')[-1]))

'''
def my_plot(a):
    mpl.rcParams.update({'font.size': 60})
    mpl.rcParams['axes.linewidth'] = 4
    plt.rcParams["font.family"] = "Times New Roman"
    label_size = 60
    axes = plt.gca()
    axes.set_ylim([0,350])
    axes.set_xlim([0,240])
    axes.tick_params(length=16, width=4)
    axes.locator_params(nbins=4, axis='y')
    plt.gcf().subplots_adjust(bottom=0.18, left = 0.18)
    plt.xlabel('Time (seconds)', fontsize = label_size)
    plt.ylabel('Bandwidth (MBits/second)', fontsize = label_size)
    plt.plot(a)
    plt.show()
'''
def main(args):
    DELTA = int(args.delta)              # number of seconds between requests
    lambdas = int(args.wavelengths)      # total labdas to allocate durring experiment
    TEST_DURRATION = DELTA * (lambdas)

    reqs_sent = 0 # updated throughout experiment

    perf_clients = []
    print("# Start iperf3 clients")
    for s in PERF_CLIENTS:
        server_addr = PERF_SERVERS[s]['address']
        client_addr = PERF_CLIENTS[s]['address']
        print("Starting Perf client on {}, connecing to {}".format(client_addr, server_addr))
        p = Process(target = start_perf_client, args = (server_addr, client_addr, TEST_DURRATION))
        p.start()
        perf_clients.append(p)

    thread_reqs = [] # list of threads

    ### THIS IS IT BOYS ###
    print("# Starting lambda experiment")
    sleep(1)
    target = None
    for l in range(lambdas):
        if l < 2:
            print("Sending request in {} seconds.".format(DELTA))
            sleep(DELTA)
        print("# Sending request to activate lambda now")
        t = client_thread()
        thread_reqs.append(t)
        sleep(10)
        print("## Lambda Requests submitted")
    print("No requests to send. Sleeping for {} seconds".format(DELTA))
    sleep(DELTA)

    print("*~*~*~*~*~*~ vFiber Client Finishing*~*~*~*~*~*~")

    for t in thread_reqs:
        t.join()

    print("*~*~*~*~*~*~ Perf Clients Finishing*~*~*~*~*~*~")

    for p in perf_clients:
        p.join()

    print("*~*~*~*~*~*~ Experiment Compete *~*~*~*~*~*~")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delta", help="Number of seconds between adding lambdas.", dest="delta", default=120, type=int)
    parser.add_argument("-w", "--wavelengths", help="Number of lambdas to run experiment with.", dest="wavelengths", default=1, type=int)

    args = parser.parse_args()
    main(args)
