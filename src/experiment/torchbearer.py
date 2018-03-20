import pexpect
import sys
import re
from a_timer import Timer
from time import sleep

'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28", request_size = 1):
    megabytes = request_size
    bits = megabytes * 8 * 1000000
    # what percent of 125 is the request
    # ports are GigabitEthernet, so max bandwithd is 125 megabytes.
    request = int(float(megabytes) // 125 * 100) # request expressed as percent of max bandwidth.

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
            '''
            Is port on or off? If port is off, turn on and set bandwidth limit to requested limit.
            If it is on, find the rate limit and increase it appropriatly.
            '''
            child.sendline("show running-config int {}".format(switch_port))
            status = child.read()
            if "shutdown" in status:
                rate = 0
                child.sendline('configure terminal')
                child.expect('\(config\)#')
                child.sendline('interface %s' % (p))
                o = child.expect(['\(config-if\)#', '% Invalid'])
                if o != 0:
                    raise Exception("Unknown switch port '%s'" % (port))
                child.sendline('no shutdown')
                child.expect('\(config-if\)#')
            else:
                child.sendline("show mls qos interface {} queueing | include bandwidth".format(swith_port))
                rate_description = child.read();
                rate = int(re.findall("\d+", rate_description)[0])
                child.expect('#')
                child.sendline('configure terminal')
                child.expect('\(config\)#')
                child.sendline('interface %s' % (p))
                o = child.expect(['\(config-if\)#', '% Invalid'])
                if o != 0:
                    raise Exception("Unknown switch port '%s'" % (port))
            new_rate = rate + request
            assert new_rate <= 100
            if new_rate > 90:
                child.sendline('no srr-queue bandwidth limit')
                child.expect('\(config-if\)#')
            elif new_rate >= 10:
                child.sendline('srr-queue bandwidth limit {}'.format(new_rate))
                child.expect('\(config-if\)#')
            else:
                raise Exception("Error encoutered allocating bandwidth on port {}".format(p))
        except AssertionError:
            raise Exception("Error configuring switch port")
            child.sendline("show mls qos interface {} queueing | include bandwidth".format(p))
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
                child.sendline('interface %s' % (swith_port))
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

def fast_off_and_on(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
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
