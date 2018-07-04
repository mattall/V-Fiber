import pexpect
import re
import sys
import argparse
from a_timer import Timer
from torchbearer import light_path, extinguish_path
from multiprocessing import Process

file_num = 0

def ping(host, time):
    global file_nun
    count = time * 10 # send ten requests per second
    outfile = "ping_{}".format(file_num)
    with open(outfile, 'w') as fout:
        subprocess.call(["ping", "host", "-i 0.1" "-c {}".format(count)], stdout = fout)
    file_num += 1

def main(args):
    endpoint = args.endpoint
    runs = args.runs # number of times to run experiment
    debug = True if args.debug == 'y' else False
    delta = args.wait
    print("running experiment \n endpoint = {} \n runs = {} \n debug = {} \
             delta = {}".format(endpoint, runs, debug, delta))

    test_interfaces = [("192.168.57.200", "GigabitEthernet 0/25"),
                                    ("192.168.57.201","GigabitEthernet 0/25")]

    # extinguish all paths to endpoint
    extinguish_path(ip_port_pairs = [("192.168.57.200", "GigabitEthernet 0/25"), ("192.168.57.201","GigabitEthernet 0/25"),\
                    ("192.168.57.200", "GigabitEthernet 0/26"), ("192.168.57.201","GigabitEthernet 0/26"),\
                    ("192.168.57.200", "GigabitEthernet 0/27"), ("192.168.57.201","GigabitEthernet 0/27"),\
                    ("192.168.57.200", "GigabitEthernet 0/28"), ("192.168.57.201","GigabitEthernet 0/28")],\
                    save = False, password = "cisco", disply_output = False)

    sleep(2)

    # light one end-to-end path
    light_path(test_interfaces)

    # begin experiment
    for _ in range(runs):
        p = Process(target=ping, args=(endpoint, delta))
        e = Process(target=extinguish, args=(path))
        l = Process(target=light_path, args=(test_interfaces))
        p.start()
        e.start()
        e.joint()
        l.start()
        sleep(delta)
        l.join()
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

    from numpy import mean, std
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
