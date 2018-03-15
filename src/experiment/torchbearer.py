import pexpect
import sys
import re
from a_timer import Timer

'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
    switches = ips
    switch_pw = "cisco"
    swith_port = port
    verbose = False

    for addr in switches:
        try:
            child = pexpect.spawn('telnet %s' % (addr))
            if verbose:
                child.logfile = sys.stdout
            child.timeout = 4
            child.expect('Password:')
        except pexpect.TIMEOUT:
            raise Exception("Couldn't log on to the switch")

        try:
            child.sendline(switch_pw)
            child.expect('>')
            child.sendline('term length 0')
            child.expect('>')
            child.sendline('enable')
            child.expect('Password:')
            child.sendline(switch_pw)
            child.expect('#')
            child.sendline('conf t')
            child.expect('\(config\)#')
            child.sendline('int %s' % (swith_port))
            child.expect('\(config-if\)#')
            child.sendline('no shut')
            child.expect('\(config-if\)#')
            child.sendline('end')
            child.expect('#')
            child.sendline('wr mem')
            child.expect('[OK]')
            child.expect('#')
            child.sendline('quit')
        except (pexpect.EOF, pexpect.TIMEOUT), e:
            child.close()
            raise Exception("Error while trying to move the vlan on the switch.")

def extinguish_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
        switches = ips
        switch_pw = "cisco"
        swith_port = port
        verbose = True

        for addr in switches:
            try:
                child = pexpect.spawn('telnet %s' % (addr))
                if verbose:
                    child.logfile = sys.stdout
                child.timeout = 4
                child.expect('Password:')
            except pexpect.TIMEOUT:
                raise Exception("Couldn't log on to the switch")

            try:
                child.sendline(switch_pw)
                child.expect('>')
                child.sendline('term length 0')
                child.expect('>')
                child.sendline('enable')
                child.expect('Password:')
                child.sendline(switch_pw)
                child.expect('#')
                child.sendline('conf t')
                child.expect('\(config\)#')
                child.sendline('interface %s' % (swith_port))
                child.expect('\(config-if\)#')
                child.sendline('shut')
                child.expect('\(config-if\)#')
                child.sendline('end')
                child.expect('#')
                child.sendline('wr mem')
                child.expect('[OK]')
                child.expect('#')
                child.sendline('quit')
            except (pexpect.EOF, pexpect.TIMEOUT), e:
                child.close()
                raise Exception("Error while trying to move the vlan on the switch.")

if __name__ == "__main__":
    time_log  = {}
    with Timer() as extinguishing_time:
        extinguish_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

    time_log['extinguishing_time'] = extinguishing_time.interval
    with Timer() as lighting_time:
        light_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

    time_log['lighting_time'] = lighting_time.interval

    for k, v in time_log.items():
        print("{15}: {}".format(k, v))
