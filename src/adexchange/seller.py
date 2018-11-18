import gzip
from settings import CONTEXT, TEST_PARAMS, SELLER
import networkx as nx
from common import get_logger
from pysyncobj import SyncObj, replicated_sync, replicated, SyncObjConf
from pysyncobj.batteries import ReplLockManager

class Seller(SyncObj):
    def __init__(self, selfAddress, partnerAddresses):
        '''
        Initialize seller class
        '''
        self.__lockManager = ReplLockManager(5)         # self unlock after being held for 5 seconds
        cfg = SyncObjConf(  logCompactionMinEntries = 2147483647, 
                            logCompactionMinTime = 2147483647,
                            )
        super(Seller, self).__init__(   selfAddress,
                                        partnerAddresses, 
                                        cfg, 
                                        consumers=[self.__lockManager],
                                        )
        self.__rsp = TEST_PARAMS['server_path']
        self.__sf = TEST_PARAMS['seller_file_name']
        self.__compressed = CONTEXT['compressed_content']
        self.__sellerGraph = nx.Graph()
        self.__logger = get_logger("Seller")


    @replicated
    def populateSellerInfo(self):
        '''
        Populates seller graph with the seller information
        '''
        resource = []
        resource.append(self.__rsp)
        resource.append(self.__sf)
        zFile = None
        tFile = None

        if self.__compressed:
            zFile = gzip.open(''.join(resource)+".gz", "r+")
        else:
            zFile = open(''.join(resource), 'r')
        while True:
            line = zFile.readline()
            if line:
                if line.startswith("#"): continue
                line = line.strip()
                vals = line.split(";")
                edge_num = 0
                if len(vals) == 8:
                    point_A = vals[0].strip()
                    point_B = vals[1].strip()
                    strands = int(vals[2])
                    strand_cap = int(vals[3])
                    strand_cost = int(vals[4])
                    provider = vals[5].strip()
                    ip_A = vals[6].strip()
                    ip_B = vals[7].strip()
                    interfaces = []
                    if strands:
                        for x in range(strands):
                            line_str = zFile.readline()
                            line_str = line_str.strip()
                            strand_data = line_str.split(';')
                            interface_a = strand_data[1].strip()
                            interface_b = strand_data[2].strip()
                            interfaces.append((interface_a, interface_b))

                    self.__logger.debug("[Seller][run]Adding Link: {0}|{1} with {2} lambdas".format(point_A, point_B, len(interfaces)))
                    self.__sellerGraph.add_edge(point_A, point_B,
                                                numberOfStrands = strands, 
                                                capacityPerStrand = strand_cap,
                                                costPerStrand = strand_cost, 
                                                ISP = provider, 
                                                prefixA = ip_A,
                                                prefixB = ip_B,
                                                interfaces = interfaces,
                                                available_interfaces = interfaces[:], 
                                                allocated_interfaces = [],
                                                disconnected_interfaces = [],
                                                key = edge_num,
                                                )
                    edge_num += 1                                                

            else: # no line to read
                break

        zFile.close()
        self.__logger.info("### Seller Information populated...")

    @replicated_sync
    def lockEdgesOnPath(self, path):
        S = self.__sellerGraph
        # Discover keys for edges
        edge_keys = []
        key_to_edge = {}
        for (u,v) in zip(path[0:], path[1:]):
            edge_keys.append(S[u][v]['key'])
            key_to_edge[S[u][v]['key']] = (u, v)

        # Acquire keys 
        edge_keys.sort()
        self.__logger.debug("[Seller][lockEdgesOnPath] Aquiring locks for edge: {}".format( [key_to_edge[k] for k in edge_keys] ))
        for key in edge_keys:
            while (self.__lockManager.tryAcquire( key ) is False): 
                time.sleep(0) # yield control to another thread
            
            self.__logger.debug("[Seller][lockEdgesOnPath] Aquired lock for edge: {}".format( key_to_edge[key] ))


    @replicated_sync
    def unlockEdgesOnPath(self, path):
        self.__logger.debug("[Seller][unlockEdgesOnPath] Relinquishing hold on path {}".format(path))
        S = self.__sellerGraph
        edge_keys = []
        key_to_edge = {}
        for (u,v) in zip(path[0:], path[1:]):
            edge_keys.append(S[u][v]['key'])
            key_to_edge[S[u][v]['key']] = (u, v)
            self.__logger.debug("[Seller][unlockEdgesOnPath] Found key {} for edge {}".format(S[u][v]['key'], (u, v)))

        edge_keys.sort(reverse=True)
        # Release the keys
        self.__logger.debug("[Seller][unlockEdgesOnPath] Releasing locks for edge: {}".format( [key_to_edge[k] for k in edge_keys] ))
        for key in edge_keys:
            self.__lockManager.release( key )
            self.__logger.debug("[Seller][unlockEdgesOnPath] Released lock for edge: {}".format( key_to_edge[key] ))


    def getSellerGraph(self):
        '''
        Returns a graph with all the seller information in it
        '''
        return self.__sellerGraph

    @replicated_sync
    def release_strand(self, u, v, num_to_release):
        # update edge info
        self.__sellerGraph[u][v]['numberOfStrands'] -= num_to_release
        buyer_interface = self.__sellerGraph[u][v]['available_interfaces'].pop()
        self.__sellerGraph[u][v]['allocated_interfaces'].append(buyer_interface)

        # send list of two ip/port pairs for link
        link_a = (self.__sellerGraph[u][v]['prefixA'], buyer_interface[0])
        link_b = (self.__sellerGraph[u][v]['prefixB'], buyer_interface[1])
        resource = [link_a, link_b]
        return resource

    @replicated_sync
    def find_edge_from_ip_port_pair(self, ip_port_pair):
        '''
        returns the node tuple (a , b) associated with a particular ip_port 
        port pair
        '''
        self.__logger.debug("[Seller][find_edge_from_ip_port_pair] Looking for edge containg {}.".format(ip_port_pair))
        ip, port = ip_port_pair
        G = self.__sellerGraph.edges
        for source, dest in self.__sellerGraph.edges:
            edge_attributes = self.__sellerGraph[source][dest]
            edge_ips = edge_attributes['prefixA'], edge_attributes['prefixB']
            if ip in edge_ips:
                # get the index of the address in the tuple
                i = edge_ips.index(ip)
                self.__logger.debug("[Seller][find_edge_from_ip_port_pair] Found IP Address on edge.".format(ip_port_pair))
                interfaces = edge_attributes['interfaces']
                self.__logger.debug("[Seller][find_edge_from_ip_port_pair] Edge contains the following interfaces: {}.".format(interfaces))
                # find the interface pair who's port shows up in the same index as the ip address
                for inter in interfaces:
                    if port == inter[i]:
                        return source, dest, inter
                    
        self.__logger.info("[Seller][find_edge_from_ip_port_pair] Edge not found for {}.".format(ip_port_pair))

                

    @replicated_sync
    def update_disconnected_strand(self, u, v, interfaces):
        '''
        Called when monitor notices a broken link
        Returns the resource spec for vFiber to extinguish the path
        '''
        self.__logger.info("[Seller][update_disconnected_strand] Interface {} down between {} and {}".format(interfaces, u, v))
        # Remove strand from allocated and put it in disconnected
        if interfaces in self.__sellerGraph[u][v]['allocated_interfaces']:
            self.__logger.debug("[Seller][update_disconnected_strand] Interface found in allocated_interfaces")
            self.__sellerGraph[u][v]['allocated_interfaces'].remove(interfaces)
            self.__sellerGraph[u][v]['disconnected_interfaces'].append(interfaces)
            link_a = (self.__sellerGraph[u][v]['prefixA'], interfaces[0])
            link_b = (self.__sellerGraph[u][v]['prefixB'], interfaces[1])
            resource = [link_a, link_b]
            return resource

        
        elif interfaces in self.__sellerGraph[u][v]['available_interfaces']:
            self.__logger.debug("[Seller][update_disconnected_strand] Interface found in available_interfaces")
            self.__sellerGraph[u][v]['available_interfaces'].remove(interfaces)
            self.__sellerGraph[u][v]['disconnected_interfaces'].append(interfaces)
            link_a = (self.__sellerGraph[u][v]['prefixA'], interfaces[0])
            link_b = (self.__sellerGraph[u][v]['prefixB'], interfaces[1])
            resource = [link_a, link_b]
            return resource
            
        else:
            self.__logger.debug("[Seller][update_disconnected_strand] Interface not found.")

    @replicated_sync
    def aquire_strand(self, u, v, num_to_release):
        # update edge info
        self.__sellerGraph[u][v]['numberOfStrands'] += num_to_release
        buyer_interface = self.__sellerGraph[u][v]['available_interfaces'].pop()
        self.__sellerGraph[u][v]['allocated_interfaces'].append(buyer_interface)

        # send list of two ip/port pairs for link
        link_a = (self.__sellerGraph[u][v]['prefixA'], buyer_interface[0])
        link_b = (self.__sellerGraph[u][v]['prefixB'], buyer_interface[1])
        resource = [link_a, link_b]
        return resource
