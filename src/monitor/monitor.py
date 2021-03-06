# monitor a link -- 
import socket
import pexpect
import sys
import re
from time import sleep
#from pysyncobj import SyncObj, replicated_sync, replicated, SyncObjConf
#from Seller import getSellerGraph, update_disconected_strand
from base.model.datamodel import Request, Data, Utility
#from realdeployment import light_path, extinguish_path
from settings import CONTEXT, SERVER_BINDING, TEST_PARAMS



#from adexchange.seller import Seller

class Monitor():
    '''
    check the interface for an occupied link. 
    If it is down, then activate an alternative link.
    '''
    def __init__(self, switch_addr):
        # cfg = SyncObjConf(logCompactionMinEntries = 2147483647, logCompactionMinTime = 2147483647)
        #     super(Seller, self).__init__(selfAddress, partnerAddresses, cfg)
        self.interval = 1 # seconds
        self.tolerance = 5 # number of times to recognize a disconnect before reporting
        self.__switch_addr = switch_addr
        self.__request_code = 102
        self.__request_type = 'MONITOR'
        self.__serverhosts = SERVER_BINDING['address'][0]
        self.__serverport = int(SERVER_BINDING['port'])
        print("Hello")

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
    


    def start_monitor(self):
        '''
        Thread handler
        '''
        print('starting monitor')
        conn = None
        ports = ['Gi 0/25',
                         'Gi 0/26',
                         'Gi 0/27',
                         'Gi 0/28',]
        stop_count = [0 for x in range(len(ports))]
        try: 
            # Request creation
            conn = self.login_to_switch(self.__switch_addr, False)
            while 1:
                if conn == -1:
                    print("Error connecting")
                    break
                
                for i in range(len(ports)):
                    p = ports[i]
                    conn, disconnected = self.link_disconnected(conn, p)
                    print("link {} disconnected: {}".format(p, disconnected))
                    if disconnected:
                        stop_count[i] += 1
                        print("stop count: ", stop_count)
                        if stop_count[i] == self.tolerance:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            try:
                                sock.connect((self.__serverhosts, self.__serverport))
                            except Exception as e:
                                print(e)
                                print("host :", self.__serverhosts)
                                print("port :", self.__serverport)

                            print("link {} disconnected: {}".format(p, disconnected))
                            data = Request( self.__request_type,
                                            self.__request_code,
                                            (self.__switch_addr, p))
                            sock.sendall(data.to_json())
                            print(data.to_json())
                            del ports[i]
                            del stop_count[i]

                    else:
                        stop_count[i] = 0
                sleep(self.interval)

        except Exception as e:
            print(e)

        finally:
            if conn:
                conn.close()

        print("ending monitor")

    '''
    def start_monitor(self):
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
                        if link_disconnected(connection, local_interface):
                            G.update_disconected_strand(u, v, ui)                            
                            extinguish_path([(ipA, local_interface), (ipB, remote_interface)])
                            if G[u][v]['available_interfaces']:
                                new_link = G.release_strand(u, v, 0)
                                light_path(new_link)

                    connection.close()
    '''
