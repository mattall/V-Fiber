import pexpect
import sys
import re
if __name__ == "__main__":
    from a_timer import Timer
from time import sleep
import argparse


'''
Toarchbearer lights an end-to-end path of dark fiber
'''
def light_path(ip_port_pairs = [("192.168.57.200", "GigabitEthernet 0/28"), ("192.168.57.201","GigabitEthernet 0/28")],
                save = False, password = 'cisco', disply_output = True):
    switch_pw = password
    verbose = disply_output


    for switch_addr, switch_port in ip_port_pairs:
        try:
            child = pexpect.spawn('telnet %s -s 192.168.57.7' % (switch_addr))
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
            if save:
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
                                        save = False, password = "cisco", disply_output = True):
    ''' Doesn't write config to memory if save is False '''

    switch_pw = password
    verbose = disply_output

    for switch_addr, switch_port in ip_port_pairs:
        try:
            child = pexpect.spawn('telnet %s -s 192.168.57.7' % (switch_addr))
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
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--mode", help="light path (l) or extinguish path (e)", dest="mode", type=str)
        parser.add_argument("-a1", "--address_one", help="address for first network device in link", dest="a1", type=str)
        parser.add_argument("-a2", "--address_two", help="address for second network device in link", dest="a2", type=str)
        parser.add_argument("-i1", "--interface_one", help="interface for first network device in link", dest="i1", type=str)
        parser.add_argument("-i2", "--interface_two", help="interface for second network device in link", dest="i2", type=str)
        parser.add_argument("-s", "--save", help="save configuration to NVM (y or n)", dest="save", type=str)
        parser.add_argument("-v", "--verbose", help="view network device output (y or n)", dest="verbose", type=str)
        parser.add_argument("-p", "--password", help="network device password", dest="pw", type=str)

        args = parser.parse_args()

        mode=args.mode
        address_one=args.a1
        address_two=args.address_two
        interface_one=args.i1
        interface_two=args.i2
        save=True if args.save == 'y' else False
        verbose=True if args.verbose == 'y' else False
        password=args.pw

        if mode == 'l':
            light_path(ip_port_pairs=[(address_one, interface_one), \
                                        (address_two, interface_two)],\
                        save=save, password=password, disply_output=verbose)

        elif mode =='e':
            extinguish_path(ip_port_pairs=[(address_one, interface_one), \
                                        (address_two, interface_two)],\
                        save=save, password=password, disply_output=verbose)

        else:
            print("invalid mode command, choose 'l' or 'e'")
