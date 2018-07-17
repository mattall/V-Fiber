import pexpect
import sys
import re
if __name__ == "__main__":
    from a_timer import Timer
from time import sleep

'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ip_port_pairs = [("192.168.57.200", "GigabitEthernet 0/28"), ("192.168.57.201","GigabitEthernet 0/28")], debug=False, save=False):
    switch_pw = "cisco"
    verbose = debug

    for switch_addr, switch_port in ip_port_pairs:
        try:
            child = pexpect.spawn('telnet %s' % (switch_addr))
            if verbose:
                child.logfile = sys.stdout
            child.timeout = 4
            child.expect('Password:')
        except pexpect.TIMEOUT:
            raise Exception("Couldn't log on to the switch: %s" % switch_addr)

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
            child.sendline('int %s' % (switch_port))
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

def extinguish_path(ip_port_pairs = [("192.168.57.200", "GigabitEthernet 0/25"), ("192.168.57.201","GigabitEthernet 0/25"),\
                                        ("192.168.57.200", "GigabitEthernet 0/26"), ("192.168.57.201","GigabitEthernet 0/26"),\
                                        ("192.168.57.200", "GigabitEthernet 0/27"), ("192.168.57.201","GigabitEthernet 0/27"),\
                                        ("192.168.57.200", "GigabitEthernet 0/28"), ("192.168.57.201","GigabitEthernet 0/28")],\
                                        debug = False, save = False):
    ''' Doesn't write config to memory by default '''

    switch_pw = "cisco"
    verbose = debug

    for switch_addr, switch_port in ip_port_pairs:
        try:
            child = pexpect.spawn('telnet %s' % (switch_addr))
            if verbose:
                child.logfile = sys.stdout
            child.timeout = 4
            child.expect('Password:')
        except pexpect.TIMEOUT:
            raise Exception("Couldn't log in to the switch")

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
            child.sendline('interface %s' % (switch_port))
            child.expect('\(config-if\)#')
            child.sendline('shut')
            child.expect('\(config-if\)#')
            child.sendline('end')
            child.expect('#')
            if save:
                child.sendline('wr mem')
                child.expect('[OK]')
                child.expect('#')
            child.sendline('quit')
        except (pexpect.EOF, pexpect.TIMEOUT), e:
            child.close()
            raise Exception("Error while trying to move the vlan on the switch.")



if __name__ == "__main__":
    for i in range(50):
        with Timer() as extinguishing_time:
            extinguish_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

        with Timer() as lighting_time:
            light_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

        print("extinguishing time:\n", str(extinguishing_time.interval))
        print("lighting time:\n", str(lighting_time.interval))
        sleep(40)
