import pexpect
import sys
import re

'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ips = ["192.168.57.200", "192.168.57.201"], port = "GigabitEthernet 0/28"):
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
            child.sendline('terminal length 0')
            child.expect('>')
            child.sendline('enable')
            child.expect('Password:')
            child.sendline(switch_pw)
            child.expect('#')
            child.sendline('configure terminal')
            child.expect('\(config\)#')
            child.sendline('interface %s' % (swith_port))
            child.expect('\(config-if\)#')
            child.sendline('no shutdown')
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
