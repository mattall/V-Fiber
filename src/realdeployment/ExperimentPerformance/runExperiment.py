import argparse
from itertools import cycle
import matplotlib.pyplot as plt
import time
import numpy as np
import re
import random
import paramiko

def do_ssh(urn, keyFile, username, password):
    # k = paramiko.RSAKey.from_private_key_file(keyFile)
    url, port = urn.split("##")
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname = url, username = username, look_for_keys=False, port=int(port))
    return c

def closeConnections(connections):
    for node, conn in connections.items():
        conn.close()
        print "Connection to {0} closed!".format(node)

def reservoir_sampling(iterator, K):
        result = []
        N = 0
        for item in iterator:
            N += 1
            if len(result) < K:
                result.append(item)
            else:
                s = int(random.random() * N)
                if s < K:
                    result[ s ] = item
                return result

def get_pair(txt):
    re1='.*?'# Non-greedy match on filler
    re2='(\\d+)'# Integer Number 1
    rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        int1 = m.group(1)
        int1 = int(int1) + 1
        return "h{0}".format(int1)

def get_meas(txt, node):
    re1='.*?'# Non-greedy match on filler
    re2='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'# Float 1
    re3='.*?'# Non-greedy match on filler
    re4='[+-]?\\d*\\.\\d+(?![-+0-9\\.])'# Uninteresting: float
    re5='.*?'# Non-greedy match on filler
    re6='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'# Float 2

    rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        float1=m.group(1)
        float2=m.group(2)
        index = None
        if "-" in float1:
            index = float(float1) * -1
        else:
            index = float(float1)
        return "{0},{1},{2}".format(index, node, float(float2))
    else:
        return None

def get_meas2(txt, node):
    re1='.*?'# Non-greedy match on filler
    re2='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'# Float 1
    re3='.*?'# Non-greedy match on filler
    re4='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'# Float 2

    rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        float1=m.group(1)
        float2=m.group(2)
        index = None
        if "-" in float1:
            index = float(float1) * -1
        else:
            index = float(float1)
        return "{0},{1},{2}".format(index, node, float(float2))
    else:
        return None

def main(args):
    nodeList = {}
    print "Connecting..."
    # FIXME (later): use geni-lib and read directly from the slice
    with open("Nodes-{0}.txt".format(args.number), "r") as fH:
        for line in fH:
            line = line.strip()
            node, urn = line.split(":")
            nodeList[node] = urn

    #################################
    # Step 1: Establish connections
    # Odd numbered are source nodes and even numbered are destinations
    ################################
    connections = {}
    sources = {}
    destinations = {}
    paths = {}
    for node, urn in nodeList.items():
        connObject = do_ssh(urn, args.keyFile, args.username, args.password)
        connections[node] = connObject
        if "-s" in node:
            sources[node] = connObject
        elif "-d" in node:
            destinations[node] = connObject
        else:
            paths[node] = connObject
        print "Node '{0}' connected using '{1}'".format(node, urn)
    print "Experiment contains {0} sources, {1} destinations, and {2} paths.".format(len(sources), len(destinations), len(paths))

    #################################
    # Step 2: Run experiments logic
    #################################
    '''
    print "\nRunning experiments..."

    # Bring interface down randomly in all but one path
    toBringDown = reservoir_sampling(paths, args.number - 1)
    for node in toBringDown:
        stdin, stdout, stderr = paths[node].exec_command("sudo ifconfig eth1 down")
        print "Interface down in {0}.".format(node)

    # Start iPerf in destinations
    for node, conn in destinations.items():
        stdin, stdout, stderr = destinations[node].exec_command("iperf -s")
        print "Starting iPerf server in {0}.".format(node)

    # Start iPerf in sources
    for node, conn in sources.items():
        dest = get_pair(node)
        stdin, stdout, stderr = sources[node].exec_command("iperf -c {0} -t {1} -i {2} | tee out_{3}_{4}interface.txt".format(dest, args.timewait, args.interval, node, args.number))
        print "Starting iPerf client in {0}. Measurements sent to {1}.".format(node, dest)

    # Bring interface up in the same path
    for node in toBringDown:
        time.sleep(args.intfUpTime)
        stdin, stdout, stderr = paths[node].exec_command("sudo ifconfig eth1 up")
        print "Interface up in {0}.".format(node)

    # FIXME (later): Actually we need to use channel.recv_exit_status() for this
    # Since everything is nested in loops above, I am going for this hack
    print "\nEntering time wait..."
    time.sleep(args.timewait)
    '''

    # Get results, clean them up and plot
    output = {}
    for node, conn in sources.items():
        print "Collecting measurements from {0}.".format(node)
        # sftp = paramiko.SFTPClient.from_transport(conn.get_transport())
        # filepath = '/users/{0}/out_{1}_{2}interface.txt'.format(args.username, node, args.number)
        localpath = 'Output/out_{0}_{1}interface.txt'.format(node, args.number)
        # sftp.get(filepath, localpath)
        # sftp.close()

        with open(localpath, "r") as fH:
            lines = fH.readlines()[6:]
        output[node] = lines

    cleanedMeas = []
    for node, out in output.items():
        for l in out[:-1]:
            line = get_meas(l.strip(), node.split("-")[0])
            if line:
                cleanedMeas.append(line)
            else:
                line = get_meas2(l.strip(), node.split("-")[0])
                cleanedMeas.append(line)

    x = np.array(cleanedMeas)
    lines = ["-","--","-.",":"]
    linecycler = cycle(lines)
    for i in np.split(x, args.number):
        indexList = []
        valueList = []
        legend = None
        for elem in i:
            index, legend, value = elem.split(",")
            indexList.append(float(index))
            valueList.append(float(value))
        plt.plot(indexList,valueList,next(linecycler),label=legend, linewidth=3)
    plt.xlabel("Time (s)", size = 17)
    plt.ylabel("Throughput (Mbps)", size = 17)
    plt.legend(loc='lower right')
    plt.savefig("Figures/Output-{0}.eps".format(args.number), format='eps', dpi=600)

    #################################
    # Step 3: Finally close all connections
    #################################
    print "\nTearing down..."
    for node, conn in destinations.items():
        stdin, stdout, stderr = destinations[node].exec_command("killall iperf")
    closeConnections(connections)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", help="Number of interfaces.", dest="number", type=int)
    parser.add_argument("-k", "--key", help="Key file.", dest="keyFile")
    parser.add_argument("-u", "--username", help="Username.", dest="username")
    parser.add_argument("-p", "--password", help="Password.", dest="password")
    parser.add_argument("-w", "--timewait", help="Time to wait/testing time.", dest="timewait", type=int)
    parser.add_argument("-i", "--interval", help="Interval for iPerf.", dest="interval", type=int)
    parser.add_argument("-l", "--intfuptime", help="Time to bring up links.", dest="intfUpTime", type=int)
    args = parser.parse_args()

    main(args)
