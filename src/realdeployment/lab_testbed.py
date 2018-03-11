import pexpect
import sys
import re

'''
script modified from Ferry Boender's blog
https://www.electricmonk.nl/log/2014/07/26/scripting-a-cisco-switch-with-python-and-expect/
'''
def addLink(switch_ip, megabytes):
    switch_ip = "192.168.57.200"
    switch_pw = "cisco"

    port_in = "GigabitEthernet 0/1"
    port_out = "GigabitEthernet 0/28"
    ports = [port_in, port_out]

    #vlan_id = 100
    verbose = True
    # subnet = "192.168.57."
    suffix = str(2)
    megabytes = 25 # megabytes demanded
    bits = megabytes * 8 * 1000000
    # what percent of 125 is the request
    # ports are GigabitEthernet, so max bandwithd is 125.
    request = int(float(megabytes) // 125 * 100)

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
        child.sendline('configure terminal')
        child.expect('\(config\)#')

        # Create a vlan
        # try:
        #     child.sendline('int vlan %d', vlan_id)
        #     o = child.expect(['\(config-if\)#', '% Invalid'])
        #     if o != 0:
        #         raise Exception("invalid vlan number '%s', must be 1 - 4094." % (port))
        #     child.sendline("ip address " + subnet + suffix)
        #     o = child.expect(['\(config-if\)#', '% Invalid'])
        #     if o != 0:
        #         raise Exception("Error addressing vlan")
        #     child.sendline("no shut")
        #     child.expect('\(config-if\)#')
        #     child.sendline("end")
        #     child.expect('\(config\)#')
        #     # try:
        #     #     child.sendline("rate-lime input {} {} {} conform-action transmit exceed-action drop".format(bits, bits/2000, bits/2000))
        #     #     child.expect('\(config-if\)#')
        #     #     child.sendline("rate-lime output {} {} {} conform-action transmit exceed-action drop".format(bits, bits/2000, bits/2000))
        #     #     child.expect('\(config-if\)#')
        #     #     child.sendline("end")
        #     #     child.expect('\(config\)#')
        #     # except:
        #     #     raise Exception("Error assigning bitrate on vlan")
        # except:
        #     raise Exception("Error creating vlan.")

        # Allowing Vlan on interface
        for p in ports:
            child.sendline("show mls qos interface {} queueing | include bandwidth".format(p))
            rate_description = child.readline();
            rate = re.finall("\d+", rate_description)[0]
            child.expect('\(config\)#')
            child.sendline('interface %s' % (p))
            o = child.expect(['\(config-if\)#', '% Invalid'])
            if o != 0:
                raise Exception("Unknown switch port '%s'" % (port))
            # child.sendline('switchport access vlan %s' % (vlan_id))
            child.expect('\(config-if\)#')
            child.sendline('no shutdown')
            child.expect('\(config-if\)#')
            try:
                new_rate = rate + request
                assert new_rate <= 100
                if new_rate > 90:
                    child.sendline('no srr-queue bandwidth limit')
                    child.expect('\(config-if\)#')
                elif new_rate >= 10
                    child.sendline('srr-queue bandwidth limit {}'.format(new_rate))
                    child.expect('\(config-if\)#')
                else:
                    raise Exception("Error encoutered allocating bandwidth on port {}".format(p))
            except AssertionError:
                raise Exception("requested bandwidth not available")
                child.sendline("show mls qos interface {} queueing | include bandwidth".format(p))
            child.sendline('wr mem')
            child.expect('[OK]')
            child.expect('#')
            child.sendline('quit')
    except (pexpect.EOF, pexpect.TIMEOUT), e:
        raise error("Error while trying to increase bandwidth on switch.")
