import pexpect

switch_ip = "192.168.57.200"
switch_pw = "cisco"
port_in = "GigabitEthernet 0/1"
port_out = "GigabitEthernet 0/28"
vlan_id = 100

child = pexpect.spawn("telnet %s", switch_ip)
child.logfile = sys.stdout
child.timeout = 4
verbose = True


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
    '''
    child.sendline('conf t')
    child.expect('\(config\)#')
    child.sendline('interface %s' % (port))
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
    '''
    child.expect('#')
    child.sendline('quit')

except (pexpect.EOF, pexpect.TIMEOUT), e:
    raise error("Error while trying to move the vlan on the switch.")
