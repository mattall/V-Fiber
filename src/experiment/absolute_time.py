import argparse
from multiprocessing import Process
from subprocess import call
from numpy import mean, std
from time import sleep
from exp_utilities import get_ssh_connection, do_ssh_and_send_command
import shlex
from base.client.tcpclient import TCPClient
from server_details import SERVERS


def ping(always_on, source, dest, time, file_num):
    print("starting ping, file_num = {}").format(file_num)
    count = time * 10 # send ten requests per second
    if always_on:
        outfile = "./absolute_time/ping_controled_{}".format(file_num)

    else:
        outfile = "./absolute_time/ping_test_{}".format(file_num)

    with open(outfile, 'w') as fout:
        cmd = "ping -i 0.1 -c {} -S {} {}".format(count, source, dest)
        print "Executing command: %s" % cmd
        call(shlex.split(cmd), stdout = fout, stderr = fout)

    print('ping finished, file_num = {}'.format(file_num))

def client_thread(req=1, req_path = None, req_file = None):
    print("Thread is initializing client with totalReqs = {}, buyer_data = {}".format(req, req_file))
    client = TCPClient()
    client.start()
    return client

def light_path((sshConnObject, debug, addr1, addr2, int1, int2, password)):
    print("lighting path")
    stdin, stdout, stderr = sshConnObject.exec_command("cd /home/matt/vFiber/V-Fiber/src/experiment; source ../../../bin/activate; python /home/matt/vFiber/V-Fiber/src/experiment/torchbearer.py -m l -a1 {} -a2 {} -i1 '{}' -i2 '{}' -s n -v y -p {}".format(addr1, addr2, int1, int2, password))
    if debug:
        print stdout.read()
        print stderr.read()

def extinguish_path((sshConnObject, debug, addr1, addr2, int1, int2, password)):
    print("extinguishing path")
    stdin, stdout, stderr = sshConnObject.exec_command("cd /home/matt/vFiber/V-Fiber/src/experiment; source ../../../bin/activate; python /home/matt/vFiber/V-Fiber/src/experiment/torchbearer.py -m e -a1 {} -a2 {} -i1 '{}' -i2 '{}' -s n -v y -p {}".format(addr1, addr2, int1, int2, password))
    if debug:
        print stdout.read()
        print stderr.read()

def restart_servers():
    server_procs = []
    for s in SERVERS:
        print('='*30)
        user = SERVERS[s]['user']
        addr = SERVERS[s]['address']
        pw = SERVERS[s]['password']
        command = "killall -9 python; cd /home/matt/vFiber/V-Fiber/src; source ../../bin/activate; python startVFCluster.py {}".format(s)
        print("executing command: {}".format(command))
        p = Process(target = do_ssh_and_send_command, args = (user, addr, pw, command))
        p.start()
        server_procs.append(p)

    sleep(10)
    return server_procs

def kill_servers():
    server_procs = []
    for s in SERVERS:
        print('='*30)
        user = SERVERS[s]['user']
        addr = SERVERS[s]['address']
        pw = SERVERS[s]['password']
        command = "killall -9 python"
        print("executing command: {}".format(command))
        p = Process(target = do_ssh_and_send_command, args = (user, addr, pw, command))
        p.start()
        server_procs.append(p)


def main(args):
    sourcepoint = '192.168.60.35'
    endpoint = args.endpoint
    runs = args.runs # number of times to run experiment
    debug = True if args.debug == 'y' else False
    delta = args.wait
    time_between_extinguish_and_light = args.time_between_extinguish_and_light


    print("running experiment \n endpoint = {} \n runs = {} \n debug = {} \n delta = {}".format(endpoint, runs, debug, delta))

    ssh = get_ssh_connection('matt', '192.168.57.102', 'onrgserver1')
    test_tuples = [(ssh, debug, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/25", "GigabitEthernet 0/25", "cisco"),
                    (ssh, debug, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/26", "GigabitEthernet 0/26", "cisco"),
                    (ssh, debug, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/27", "GigabitEthernet 0/27", "cisco"),
                    (ssh, debug, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/28", "GigabitEthernet 0/28", "cisco")]

    #Connect to GC Servers

    sleep(5)


    for tt in test_tuples:
        extinguish_path(tt)
        sleep(5)

    print("*~* Link Benchmark Test Beginning (path ignighting and extinguishing) *~*")
    always_on = False
    file_num = 0
    # begin experiment
    for i in range(runs):
        restart_servers()
        p = Process(target=ping, args=(always_on, sourcepoint, endpoint, delta, file_num))
        file_num += 1
        p.start()
        t = client_thread()
        sleep(time_between_extinguish_and_light)
        t.join()
        p.join()
        for tt in test_tuples:
            extinguish_path(tt)
            sleep(5)
        kill_servers()


    ssh.close()

    messages_sent = delta*10*runs

    # Count the number of time out messages in each ping file
    files = ["absolute_time/ping_test_{}".format(x) for x in range(file_num)]
    timeouts = []
    for f in files:
        print("f = {}".format(f))
        with open(f,'r') as ping_file:
            ping_data = ping_file.readlines()

        timeout_count = 0
        for line in ping_data:
            if "Request timeout for icmp_seq" in line:
                timeout_count += 1

        timeouts.append(timeout_count)

    times = [(float(tc)/10.0)-time_between_extinguish_and_light for tc in timeouts]
    average = mean(times)
    standard_deviation = std(times)
    print("mean: {}".format(average))
    print("standard deviation: {}".format(standard_deviation))
    with open("./absolute_time/0_ping_test_Results", 'w') as resultsFile:
        resultsFile.write("messages set: {}\n".format(messages_sent))
        resultsFile.write("mean time to activate: {} seconds \n".format(average))
        resultsFile.write("standard deviation: {} seconds".format(standard_deviation))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="Network Endpoint.", dest="endpoint", type=str)
    parser.add_argument("-r", "--runs", help="Number of trials to run.", dest="runs", type=int)
    parser.add_argument("-d", "--debug", help="Show messages. (y or n)", dest="debug", type=str)
    parser.add_argument("-w", "--wait", help="Number of seconds to wait between runs", type=int)
    parser.add_argument("-t", "--time_between_extinguish_and_light", dest="time_between_extinguish_and_light", help="Number of seconds to wait after sending a ping and extinguishing a path before lighting it again", default = 5 , type=int)
    args = parser.parse_args()

    main(args)
