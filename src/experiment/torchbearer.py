import pexpect
import sys
import re
from a_timer import Timer
from time import sleep
'''
from torchbearer import light_path as lp
from torchbearer import extinguish_path as ep
'''
'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28", request_size = 25):
    megabytes = request_size
    # bits = megabytes * 8 * 1000000
    # what percent of 125 is the request
    # ports are GigabitEthernet, so max bandwithd is 125 megabytes.
    request = int(megabytes / 125.0 * 100) # request expressed as percent of max bandwidth.

    switches = ips
    switch_pw = "cisco"
    switch_port = port
    verbose = True

    for addr in switches:
        try:
            try:
                child = pexpect.spawn('telnet %s' % (addr), maxread=1)
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
                '''
                Is port on or off? If port is off, turn on and set bandwidth limit to requested limit.
                If it is on, find the rate limit and increase it appropriatly.
                '''
                child.sendline("show running-config int {}".format(switch_port))
                index = child.expect(['shutdown', '#'])
                if index == 0: # port is shutdown.
                    rate = 0
                    child.sendline('configure terminal')
                    child.expect('\(config\)#')
                    child.sendline('interface %s' % (switch_port))
                    o = child.expect(['\(config-if\)#', '% Invalid'])
                    if o != 0:
                        raise Exception("Unknown switch port '%s'" % (switch_port))
                    child.sendline('no shutdown')
                    child.expect('\(config-if\)#')

                elif index == 1: # port is not shutdown
                    child.sendline("show mls qos interface {} queueing | include bandwidth".format(switch_port))
                    child.expect('\d+')
                    data = child.read()
                    child.sendline('echo %d' % data)
                    child.expect('\(config\)#')
                    child.sendline('configure terminal')
                    child.expect('\(config\)#')
                    child.sendline('interface %s' % (switch_port))
                    o = child.expect(['\(config-if\)#', '% Invalid'])
                    if o != 0:
                        raise Exception("Unknown switch port '%s'" % (switch_port))

                else: # something bad happened
                    raise Exception("Error determining if switch port is up.")

                new_rate = rate + request
                assert new_rate <= 100
                if new_rate > 90:
                    child.sendline('no srr-queue bandwidth limit')
                    child.expect('\(config-if\)#')
                elif new_rate >= 10:
                    child.sendline('srr-queue bandwidth limit {}'.format(new_rate))
                    child.expect('\(config-if\)#')
                else:
                    raise Exception("Error encoutered allocating {} percent of bandwidth on port {}".format(new_rate, switch_port))
            except AssertionError:
                raise Exception("Error configuring switch port")
            child.sendline('end')
            child.expect('#')
            child.sendline('wr mem')
            child.expect('[OK]')
            child.expect('#')
            child.sendline('quit')
        except (pexpect.EOF, pexpect.TIMEOUT), e:
            child.close()
            raise Exception("Error while trying to move the vlan on the switch.")

def fast_extinguish_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
        ''' Doesn't write config to memory '''
        switches = ips
        switch_pw = "cisco"
        switch_port = port
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
                child.sendline('interface %s' % (switch_port))
                child.expect('\(config-if\)#')
                child.sendline('shut')
                child.expect('\(config-if\)#')
                child.sendline('end')
                child.expect('#')
                child.sendline('quit')
            except (pexpect.EOF, pexpect.TIMEOUT), e:
                child.close()
                raise Exception("Error while trying to move the vlan on the switch.")


def extinguish_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
        switches = ips
        switch_pw = "cisco"
        switch_port = port
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
                child.sendline('interface %s' % (switch_port))
                child.expect('\(config-if\)#')
                child.sendline('no srr-queue bandwidth limit')
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

def fast_off_and_on(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
    switches = ips
    switch_pw = "cisco"
    switch_port = port
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
            child.sendline('int %s' % (switch_port))
            child.expect('\(config-if\)#')
            child.sendline('shut')
            child.expect('\(config-if\)#')
            child.sendline('no shut')
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
    for i in range(50):
        with Timer() as extinguishing_time:
            fast_extinguish_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

        with Timer() as lighting_time:
            light_path(["192.168.57.200", "192.168.57.201"], "GigabitEthernet 0/28")

        print("extinguishing time:\n", str(extinguishing_time.interval))
        print("lighting time:\n", str(lighting_time.interval))
        sleep(40)
