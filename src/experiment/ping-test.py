import pexpect
import re
import sys
import argparse
from a_timer import Timer
from torchbearer import light_path, extinguish_path
from multiprocessing import Process
from subprocess import call, Popen
from numpy import mean, std
from server_details import SERVERS
from time import sleep
from exp_utilities import get_ssh_connection
import shlex

def ping(always_on, source, dest, time, file_num):
    print("starting ping, file_num = {}").format(file_num)
    count = time * 10 # send ten requests per second
    if always_on:
        outfile = "./ping_control/ping_controled_{}".format(file_num)

    else:
        outfile = "./ping_test/ping_test_{}".format(file_num)

    with open(outfile, 'w') as fout:
        cmd = "ping -i 0.1 -c {} -S {} -b vlan0 {}".format(count, source, dest)
        print "Executing command: %s" % cmd
        proc = call(shlex.split(cmd), stdout = fout, stderr = fout)

        # #WITH SOURCE ADDR
        # call(["ping", "-i 0.1", "-c {}".format(count), "-S {}".format(source), dest], stdout = fout, stderr = fout, shell = True)

        # # WITH BOUND INTERFACE
        # call(["ping", "-i 0.1", "-c {}".format(count), "-b vlan0", dest], shell=True, stdout = fout)

        # #WITHOUT SOURCE ADDR
        # call(["ping", "-i 0.1", "-c {}".format(count), dest], shell=True,stdout = fout, stderr = fout)

    print('ping finished, file_num = {}'.format(file_num))

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

def main(args):
    sourcepoint = '192.168.60.35'
    endpoint = args.endpoint
    runs = args.runs # number of times to run experiment
    debug = True if args.debug == 'y' else False
    delta = args.wait
    time_between_extinguish_and_light = args.time_between_extinguish_and_light


    print("running experiment \n endpoint = {} \n runs = {} \n debug = {} \n delta = {}".format(endpoint, runs, debug, delta))

    ssh = get_ssh_connection('matt', '192.168.57.102', 'onrgserver1')
    test_tuple = (ssh, debug, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/25", "GigabitEthernet 0/25", "cisco")

    light_path(test_tuple)
    sleep(10)

    # print("*~* Ping Controlled Test Beginning (path continuously lit) *~*")
    # sleep(delta)
    # always_on = True
    # file_num = 0
    # # begin experiment
    # for _ in range(runs):
    #     p = Process(target=ping, args=(always_on, sourcepoint, endpoint, delta, file_num))
    #     file_num += 1
    #     p.start()
    #     p.join()

    print("*~* Link Benchmark Test Beginning (path ignighting and extinguishing) *~*")
    always_on = False
    file_num = 0
    # begin experiment
    for _ in range(runs):
        p = Process(target=ping, args=(always_on, sourcepoint, endpoint, delta, file_num))
        file_num += 1
        p.start()
        sleep(1)
        extinguish_path(test_tuple)
        sleep(time_between_extinguish_and_light)
        light_path(test_tuple)
        p.join()

    ssh.close()

    messages_sent = delta*10*runs

    # # Count the number of time out messages in each ping file
    # files = ["ping_control/ping_controled_{}".format(x) for x in range(file_num)]
    # timeouts = []
    # for f in files:
    #     print("f = {}".format(f))
    #     with open(f,'r') as ping_file:
    #         ping_data = ping_file.readlines()
    #
    #     timeout_count = 0
    #     for line in ping_data:
    #         if "Request timeout for icmp_seq" in line:
    #             timeout_count += 1
    #
    #     timeouts.append(timeout_count)
    #
    # times = [float(tc)/10.0 for tc in timeouts]
    # average = mean(times)
    # standard_deviation = std(times)
    # print("mean: {}".format(average))
    # print("standard deviation: {}".format(standard_deviation))
    # with open("./ping_control/0_ping_controled_Results", 'w') as resultsFile:
    #     resultsFile.write("messages set: {}\n".format(messages_sent))
    #     resultsFile.write("mean timeouts: {}\n".format(average))
    #     resultsFile.write("standard deviation: {}".format(standard_deviation))


    # Count the number of time out messages in each ping file
    files = ["ping_test/ping_test_{}".format(x) for x in range(file_num)]
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
    with open("./ping_test/0_ping_test_Results", 'w') as resultsFile:
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
