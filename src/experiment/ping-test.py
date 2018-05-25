import pexpect
import re
import sys
from a_timer import Timer

with Timer() as t:
    child = pexpect.spawn('ping 192.168.60.2 -i 0.1')
    while 1:
        line = child.readline()
        if not line: break
        fields = line.strip().split()

        regex = re.compile("time=([-+]?[0-9]*\.?[0-9]+)")
        if regex.findall(line): break
print("time: ", t.interval)
