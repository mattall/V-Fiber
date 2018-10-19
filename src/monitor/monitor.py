# monitor a link -- 

import pexpect
import sys
import re
from time import sleep
from pysyncobj import SyncObj, replicated_sync, replicated, SyncObjConf
from Seller import getSellerGraph, update_disconected_strand
from realdeployment import light_path, extinguish_path

#from adexchange.seller import Seller

class Monitor(SyncObj):
    '''
    check the interface for an occupied link. 
    If it is down, then activate an alternative link.
    '''
    def __init__(self, selfAddress, partnerAddresses):
        cfg = SyncObjConf(logCompactionMinEntries = 2147483647, logCompactionMinTime = 2147483647)
            super(Seller, self).__init__(selfAddress, partnerAddresses, cfg)
        interval = 5 # seconds

    def login_to_switch(self, switch_addr, verbose=False):
        switch_pw = "cisco"
        verbose = verbose    
        try:
            child = pexpect.spawn('telnet %s' % (switch_addr))
            if verbose:
                child.logfile = sys.stdout
            child.timeout = 4
            child.expect('Password:')
            child.sendline(switch_pw)
            child.expect('>')
            child.sendline('term length 0')
            child.expect('>')
            child.sendline('enable')
            child.expect('Password:')
            child.sendline(switch_pw)
            child.expect('#')
            return child
        except:
            print("Exception was thrown")
            print(str(child))
            return -1

    def link_disconnected(self, conn, switch_port):
        # input: pexpect child, assumed to be connected to a network devices
        #        switch_port, the interface we are checking.
        #
        # returns True if link is up, false if link is down.
        interface_type, port_num = switch_port.split()
        conn.sendline("sho int {0} | i {1}".format(switch_port, port_num))
        status = conn.expect(['\(connected\)', '\(notconnect\)', '\(disabled\)'])
        if status == 1:
            return (conn, True)
        else:
            return (conn, False)

    def monitor(self):
        # Constantly runs, looking for broen links, and updating the seller graph when appropriate
        while True: 
            if self.__isLeader():
                G = getSellerGraph()
                for (u, v) in G:
                    ipA = G[u][v]['prefixA']
                    ipB = G[u][v]['prefixB']
                    uis = G[u][v]['allocated_interfaces']
                    try:
                        connection = login_to_switch(ipA, verbose=True)
                    except Exception as e:
                        print(e)
                        print("COULDNT LOG INTO SWITCH! QUITTING.")
                        #TODO: Maybe we should try the switch at the other end if this fails? 
                        break

                    for ui in uis:
                        (local_interface, remote_interface) = ui
                        if link_disconnected(connection, local_interface)
                            G.update_disconected_strand(u, v, ui)                            
                            extinguish_path([(ipA, local_interface), (ipB, remote_interface)])
                            if G.[u][v]['available_interfaces']:
                                new_link = G.release_strand(u, v, 0)
                                light_path(new_link)

                    connection.close()


    # conn = login_to_switch('192.168.57.200', True)
    # conn.sendline('sho int gig 0/25 | i 0/25')
    # r = conn.expect(['\(connected\)', '\(notconnect\)', '\(disabled\)'])
    '''
    possible cases for show config
    ['line protocol is up (connected)',  'line protocol is down (notconnect)', 'line protocol is down (disabled)']
    '''

