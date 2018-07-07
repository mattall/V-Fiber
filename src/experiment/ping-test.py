import pexpect
import re
import sys
import argparse
from a_timer import Timer
from torchbearer import light_path, extinguish_path
from multiprocessing import Process
from subprocess import call
from numpy import mean, std
from server_details import SERVERS
from time import sleep
from exp_utilities import get_ssh_connection

file_num = 0

def ping(host, time):
    global file_num
    count = time * 10 # send ten requests per second
    outfile = "ping_{}".format(file_num)
    with open(outfile, 'w') as fout:
        call(["ping", "host", "-i 0.1 " " -c {}".format(count)], stdout = fout)
    file_num += 1

def light_path((sshConnObject, addr1, addr2, int1, int2, password)):
    return sshConnObject.exec_command("python torchbearer.py -m l -a1 {} -a2 {} -i1 {} -i2 {} -s n -v y -p {}".format(addr1, addr2, int1, int2, password))

def extinguish_path((sshConnObject, mode, addr1, addr2, int1, int2, password)):
    return sshConnObject.exec_command("python torchbearer.py -m e -a1 {} -a2 {} -i1 {} -i2 {} -s n -v n -p {}".format(addr1, addr2, int1, int2, password))


def main(args):
    endpoint = args.endpoint
    runs = args.runs # number of times to run experiment
    debug = True if args.debug == 'y' else False
    delta = args.wait
    print("running experiment \n endpoint = {} \n runs = {} \n debug = {} \
             delta = {}".format(endpoint, runs, debug, delta))

    ssh = get_ssh_connection('matt', '192.168.57.102', 'onrgserver1')
    test_tuple = (ssh, "192.168.57.200", "192.168.57.201", "GigabitEthernet 0/25", "GigabitEthernet 0/25", "cisco")

    stdin, stdout, stderr = ssh.exec_command("cd /home/matt/vFiber/V-Fiber/src/experiment; source ../../bin/activate")
    stdin, stdout, stderr = light_path(test_tuple)
    sleep(40)
    # begin experiment
    for _ in range(runs):
        p = Process(target=ping, args=(endpoint, delta))
        p.start()
        extinguish_path(test_tuple)
        light_path(test_tuple)
        p.join()

    global file_num
    flies = ["ping_{}".format(x) for x in range(file_num)]
    times = []
    for f in files:
        f_data = [int(line.rstrip()) for line in open(f, "r")]
        for i in range(len(f_data)):
            if i == 0:
                min = f_data[i]
            elif ( f_data[i] - f_data[i - 1] ) > 1:
                max = f_data[i-1]
                times.append((max-min+1)/10.0)
                min = f_data[i]
            else: pass

    average = mean(times)
    standard_deviation = std(times)
    print("mean: {}".format(mean))
    print("standard deviation: {}".format(standard_deviation))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="Network Endpoint.", dest="endpoint", type=str)
    parser.add_argument("-r", "--runs", help="Number of trials to run.", dest="runs", type=int)
    parser.add_argument("-d", "--debug", help="Show messages. (y or n)", dest="debug", type=str)
    parser.add_argument("-w", "--wait", help="Number of seconds to wait between runs", type=int)
    args = parser.parse_args()
    print('hello')
    main(args)
