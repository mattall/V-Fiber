import geni.aggregate.instageni as IGAM
import geni.util
import logging
import random
import geni.rspec.pg as PG
from subprocess import call

'''
Get Details of all aggregates
'''
def getDetails(IG):
    for am in IG.aggregates():
        print am.name
        print am.amtype
        print am.api
        print am.component_manager_id
        print am.listresources
        print am.url
        print "\n"

'''
Return list of locations considered
'''
def getLocations():
    ###
    # Removed Utah and LSU as something is wrong with them
    # 32 locations across 19 states
    ###
    # CENIC         - California
    # NPS           - California
    # Stanford      - California
    # UCLA          - California
    # Colorado      - Colorado
    # GATech        - Georgia
    # SOX           - Georgia
    # Chicago       - Illinois
    # Illinois      - Illinois
    # Northwestern  - Illinois
    # MOXI          - Indiana
    # Kansas        - Kansas
    # Kentucky      - Kentucky
    # UKYMCV        - Kentucky
    # UKYPKS2       - Kentucky
    # MAX           - Maryland
    # GPO           - Massachusetts
    # Kettering     - Michigan
    # UMichigan     - Michigan
    # Missouri      - Missouri
    # UMKC          - Missouri
    # Cornell       - NewYork
    # NYSERNet      - NewYork
    # NYU           - NewYork
    # Princeton     - NewJersey
    # Rutgers       - NewJersey
    # CaseWestern   - Ohio
    # Clemson       - SouthCarolina
    # UTC           - Tennessee
    # UtahDDC       - Utah
    # UWashington   - Washington
    # Wisconsin     - Wisconsin

    locations = ['CENIC', 'CaseWestern', 'Chicago', 'Clemson', 'Colorado', 'Cornell', 'GATech', \
                  'GPO', 'Illinois', 'Kansas', 'Kentucky', 'Kettering', 'MAX', 'MOXI', \
                 'Missouri', 'NPS', 'NYSERNet', 'NYU', 'Northwestern', 'Princeton', 'Rutgers', 'SOX', 'Stanford', \
                 'UCLA', 'UKYMCV', 'UKYPKS2', 'UMKC', 'UMichigan', 'UTC', 'UWashington', 'UtahDDC', 'Wisconsin']
    return locations

'''
Returns a map of locations to GENI nodes
'''
def getGeniMap():
    geniMap = {
        'California': ['CENIC', 'NPS', 'Stanford', 'UCLA'],\
        'Colorado': ['Colorado'], \
        'Georgia': ['GATech'], \
        'Illinois': ['Illinois', 'Chicago', 'Northwestern'], \
        'Indiana': ['MOXI'], \
        'Kansas': ['Kansas'], \
        'Kentucky': ['Kentucky', 'UKYMCV', 'UKYPKS2'], \
        'Maryland': ['MAX'], \
        'Massachusetts': ['GPO'], \
        'Michigan': ['Kettering', 'UMichigan'], \
        'Missouri': ['Missouri', 'UMKC'], \
        'NewYork': ['Cornell', 'NYSERNet', 'NYU'], \
        'NewJersey': ['Princeton', 'Rutgers'], \
        'Ohio': ['CaseWestern'], \
        'SouthCarolina': ['Clemson'], \
        'Tennessee': ['UTC'], \
        'Utah': ['UtahDDC'], \
        'Washington': ['UWashington'], \
        'Wisconsin': ['Wisconsin']
    }
    return geniMap

'''
Print ad details at all locations
'''
def printADDetails(IG):
    locations = getLocations()
    for l in locations:
        try:
            ad = getattr(IGAM, l).listresources(context)
            logging.info(l, ad.routable_addresses.available, ad.routable_addresses.capacity)
        except:
            logging.error("Remove: ", l)

'''
Get resources in all aggregates
'''
def getResources(state, context):
    geniMap = getGeniMap()
    location = random.choice(geniMap[state])
    try:
        ad = getattr(IGAM, location).listresources(context)
        logging.info("Location {0} has {1} out of {2} addresses.".format(location, ad.routable_addresses.available, ad.routable_addresses.capacity))
        return ad
    except:
        raise ("Cannot get resources!")

'''
Generate rspec
'''
def two_nodes_rspec(context, slicename, location1, location2, ip1, ip2, port1, port2, bandwidth, location, number):
    ''' Create an RSpec for a simple two-node link'''
    interfaces = [i for i in xrange(number)]
    r = PG.Request()
    l1 = getResources(location1, context)
    l2 = getResources(location2, context)

    ip1List = []
    if "," in ip1:
        ip1List = ip1.split(",")
    else:
        ip1List.append(ip1)

    ip2List = []
    if "," in ip2:
        ip2List = ip2.split(",")
    else:
        ip2List.append(ip2)

    stub = PG.Node("ig-%s" % (location1), "emulab-xen")
    stub.component_manager_id = l1.nodes[0].component_manager_id
    # stub.addService(PG.Install(url="http://www.gpolab.bbn.com/~jbs/dingbot.tar.gz", path="/opt"))
    stub.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
    stub.exclusive = False
    stub_intf_list = []
    for i in interfaces:
        stub_intf = stub.addInterface("if{0}".format(i))
        stub_intf.addAddress(PG.IPv4Address(ip1List[i], "255.255.255.0"))
        stub_intf_list.append(stub_intf)
    r.addResource(stub)

    real = PG.Node("ig-%s" % (location2), "emulab-xen")
    real.component_manager_id = l2.nodes[0].component_manager_id
    real.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
    real.exclusive = False
    real_intf_list = []
    for i in interfaces:
        real_intf = real.addInterface("if{0}".format(i))
        real_intf.addAddress(PG.IPv4Address(ip2List[i], "255.255.255.0"))
        real_intf_list.append(real_intf)
    r.addResource(real)

    for i in interfaces:
        link = PG.Link("link{0}".format(interfaces[i]))
        link.addInterface(stub_intf_list[i])
        link.addInterface(real_intf_list[i])
        link.bandwidth = bandwidth
        r.addResource(link)

    name = location+"test-{0}-{1}-{2}.rspec".format(location1, location2, number)
    r.writeXML(name)
    return name

def two_nodes_rspec_simple(context, slicename, location1, location2, ip1, ip2, port1, port2, bandwidth, location, number):
    ''' Create an RSpec for a simple two-node link'''

    interfaces = [i for i in xrange(number)]
    r = PG.Request()

    nodeA = PG.Node("A", "emulab-xen")
    nodeA.exclusive = False
    nodeA_host_intf_list = []
    for i in interfaces:
        nodeA_host_intf = nodeA.addInterface("if_AH{0}".format(i))
        nodeA_host_intf.addAddress(PG.IPv4Address("192.165.{0}.1".format(i+1), "255.255.255.0"))
        nodeA_host_intf_list.append(nodeA_host_intf)
    r.addResource(nodeA)

    nodeB = PG.Node("B", "emulab-xen")
    nodeB.exclusive = False
    nodeB_host_intf_list = []
    for i in interfaces:
        nodeB_host_intf = nodeB.addInterface("if_BH{0}".format(i))
        nodeB_host_intf.addAddress(PG.IPv4Address("192.168.{0}.1".format(i+1), "255.255.255.0"))
        nodeB_host_intf_list.append(nodeB_host_intf)
    r.addResource(nodeB)

    for i in interfaces:
        link = PG.Link("link{0}".format(interfaces[i]))
        link.addInterface(nodeA_host_intf_list[i])
        link.addInterface(nodeB_host_intf_list[i])
        link.bandwidth = 20000
        r.addResource(link)

    name = location+"test-{0}-{1}-{2}.rspec".format(location1, location2, number)
    r.writeXML(name)
    return name

if __name__ == "__main__":
    logging.info("Did you run 'context-from-bundle --bundle ~/Downloads/omni.bundle' before this?\n")
    context = geni.util.loadContext()
    sliceName = 'bla'
    location = '/Users/ram/Desktop/RAM/Project/GreyFiber/ClientServer/src/realdeployment/'

    # getDetails(IGAM)
    # printADDetails(IGAM)
    # ad = getResources("California", context)
    rspecName = two_nodes_rspec(context, sliceName, "Wisconsin", "Missouri", "192.168.1.1", "192.168.1.2", "0", "0", 20000, location, 2)
    # call("/Applications/omniTools-2.10/stitcher.app/Contents/MacOS/stitcher createsliver %s %s" % (sliceName, rspecName), shell=True)
