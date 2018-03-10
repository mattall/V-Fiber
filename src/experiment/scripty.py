import pexpect
import sys

'''
script modified from Ferry Boender's blog
https://www.electricmonk.nl/log/2014/07/26/scripting-a-cisco-switch-with-python-and-expect/
'''

switch_ip = "192.168.57.200"
switch_pw = "cisco"
port_in = "GigabitEthernet 0/1"
port_out = "GigabitEthernet 0/28"
vlan_id = 100
verbose = True
subnet = "192.168.57."
suffix = str(2)
megabytes = 25 # megabytes
bits = megabytes * 8 * 1000000

try:
    try:
        child = pexpect.spawn('telnet %s' % (switch_ip))
        if verbose:
            child.logfile = sys.stdout
        child.timeout = 4
        child.expect('Password:')
    except pexpect.TIMEOUT:
        raise OurException("Couldn't log on to the switch")

    child.sendline(switch_pw)
    child.expect('>')
    child.sendline('terminal length 0')
    child.expect('>')
    child.sendline('enable')
    child.expect('Password:')
    child.sendline(switch_pw)
    child.expect('#')
    child.sendline('show running-config interface GigabitEthernet 0/1')
    child.sendline('conf t')
    child.expect('\(config\)#')

    # Create a vlan
    try:
        child.sendline('int vlan %d', vlan_id)
        o = child.expect(['\(config-if\)#', '% Invalid'])
        if o != 0:
            raise Exception("invalid vlan number '%s', must be 1 - 4094." % (port))
        child.sendline("ip address " + subnet + suffix)
        o = child.expect(['\(config-if\)#', '% Invalid'])
        if o != 0:
            raise Exception("Error addressing vlan")
        child.sendline("no shut")
        child.expect('\(config-if\)#')
        try:
            child.sendline("rate-lime input {} {} {} conform-action transmit exceed-action drop".format(bits, bits/2000, bits/2000))
            child.expect('\(config-if\)#')
            child.sendline("rate-lime output {} {} {} conform-action transmit exceed-action drop".format(bits, bits/2000, bits/2000))
            child.expect('\(config-if\)#')
            child.sendline("end")
            child.expect('\(config\)#')
        except:
            raise Exception("Error assigning bitrate on vlan")
    except:
        raise Exception("Error creating vlan.")

    # Allowing Vlan on interface
    child.sendline('interface %s' % (port_in))
    o = child.expect(['\(config-if\)#', '% Invalid'])
    if o != 0:
        raise Exception("Unknown switch port '%s'" % (port))
    child.sendline('switchport access vlan %s' % (vlan))
    child.expect('\(config-if\)#')
    child.sendline('no shutdown')
    child.expect('#')
    child.sendline('end')
    child.expect('#')
    child.sendline('wr mem')
    child.expect('[OK]')
    child.expect('#')
    child.sendline('quit')

except (pexpect.EOF, pexpect.TIMEOUT), e:
    raise error("Error while trying to move the vlan on the switch.")
