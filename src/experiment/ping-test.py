import argparse
from multiprocessing import Process
from subprocess import call
from numpy import mean, std
from time import sleep
from exp_utilities import get_ssh_connection
import shlex

def ping(always_on, source, dest, time, file_num):
    print("starting ping, file_num = {}").format(file_num)
    count = time * 10 # send ten requests per second
    if always_on:
        outfile = "./ping_control/ping_controlled_{}".format(file_num)

    else:
        outfile = "./ping_test1/ping_test_{}".format(file_num)

    with open(outfile, 'w') as fout:
        cmd = "ping -i 0.1 -c {} -S {} {}".format(count, source, dest)
        print "Executing command: %s" % cmd
        call(shlex.split(cmd), stdout = fout, stderr = fout)

    print('ping finished, file_num = {}'.format(file_num))

def light():
    call(["python", "torchbearer.py", "l", "-n", "True"])

def putout():
    call(["python", "torchbearer.py", "e", "-n", "True"])


def main(args):
    endpoint = args.endpoint
    runs = args.runs # number of times to run experiment
    debug = True if args.debug == 'y' else False
    delta = args.wait
    time_between_extinguish_and_light = args.time_between_extinguish_and_light

    print("running experiment \n endpoint = {} \n runs = {} \n debug = {} \n delta = {}".format(endpoint, runs, debug, delta))

    print("*~* Link Benchmark Test Beginning (path igniting and extinguishing) *~*")
    always_on = False
    
    light()
    sleep(10)
    # begin experiment
    for i in range(runs):
        p = Process(target=ping, args=(always_on, args.sourcepoint, endpoint, delta, i))
        p.start()
        putout()
        sleep(time_between_extinguish_and_light)
        light()
        p.join()
        sleep(delta)

    messages_sent = delta*10*runs
    print("messages_sent: {}".format(messages_sent))

    # Count the number of time out messages in each ping file
    files = ["ping_test1/ping_test_{}".format(x) for x in range(i)]
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
    with open("./ping_test1/0_ping_test_Results", 'w') as resultsFile:
        resultsFile.write("messages set: {}\n".format(messages_sent))
        resultsFile.write("mean time to activate: {} seconds \n".format(average))
        resultsFile.write("standard deviation: {} seconds".format(standard_deviation))
        resultsFile.write("data:\n {} ".format(times))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sourcepoint", help="Network Sourcepoint.", dest="sourcepoint", type=str)
    parser.add_argument("-e", "--endpoint", help="Network Endpoint.", dest="endpoint", type=str)
    parser.add_argument("-r", "--runs", help="Number of trials to run.", dest="runs", type=int)
    parser.add_argument("-d", "--debug", help="Show messages. (y or n)", dest="debug", type=str)
    parser.add_argument("-w", "--wait", help="Number of seconds to wait between runs", type=int)
    parser.add_argument("-t", "--time_between_extinguish_and_light", dest="time_between_extinguish_and_light", help="Number of seconds to wait after sending a ping and extinguishing a path before lighting it again", default = 5 , type=int)
    args = parser.parse_args()

    main(args)
