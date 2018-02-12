import geni.util
import logging
import geni.rspec.pg as PG
import argparse

def nodes_rspec(context, number):
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

    name = "test-{0}.rspec".format(number)
    r.writeXML(name)

if __name__ == "__main__":
    logging.info("Did you run 'context-from-bundle --bundle ~/Downloads/omni.bundle' before this?\n")
    context = geni.util.loadContext()

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", help="Number of interfaces.", dest="number", type=int)
    args = parser.parse_args()

    nodes_rspec(context, args.number)
