import geni.util
import logging
import geni.rspec.pg as PG
import argparse

def nodes_rspec(context, number):
    interfaces = [i for i in xrange(number)]
    r = PG.Request()

    nodeA = PG.Node("A", "emulab-xen")
    nodeA.addService(PG.Install(url="http://pages.cs.wisc.edu/~rkrish/GENI/ospf-script-{0}intf.tar.gz".format(2*number), path="/local"))
    nodeA.addService(PG.Execute(shell="sh", command="/local/ospf-script-{0}intf.sh".format(2*number)))
    nodeA.exclusive = False
    nodeA_host_intf_list = []
    nodeA_router_intf_list = []
    for i in interfaces:
        nodeA_host_intf = nodeA.addInterface("if_AH{0}".format(i))
        nodeA_host_intf.addAddress(PG.IPv4Address("192.165.{0}.1".format(i+1), "255.255.255.0"))
        nodeA_host_intf_list.append(nodeA_host_intf)
        nodeA_router_intf = nodeA.addInterface("if_AR{0}".format(i))
        nodeA_router_intf.addAddress(PG.IPv4Address("192.166.{0}.1".format(i+1), "255.255.255.0"))
        nodeA_router_intf_list.append(nodeA_router_intf)
    r.addResource(nodeA)

    nodeB = PG.Node("B", "emulab-xen")
    nodeB.addService(PG.Install(url="http://pages.cs.wisc.edu/~rkrish/GENI/ospf-script-{0}intf.tar.gz".format(2*number), path="/local"))
    nodeB.addService(PG.Execute(shell="sh", command="/local/ospf-script-{0}intf.sh".format(2*number)))
    nodeB.exclusive = False
    nodeB_host_intf_list = []
    nodeB_router_intf_list = []
    for i in interfaces:
        nodeB_router_intf = nodeB.addInterface("if_BR{0}".format(i))
        nodeB_router_intf.addAddress(PG.IPv4Address("192.167.{0}.1".format(i+1), "255.255.255.0"))
        nodeB_router_intf_list.append(nodeB_router_intf)
        nodeB_host_intf = nodeB.addInterface("if_BH{0}".format(i))
        nodeB_host_intf.addAddress(PG.IPv4Address("192.168.{0}.1".format(i+1), "255.255.255.0"))
        nodeB_host_intf_list.append(nodeB_host_intf)
    r.addResource(nodeB)

    router_intf_A_list = []
    router_intf_B_list = []
    host_intf_A_list = []
    host_intf_B_list = []
    for i in interfaces:
        router = PG.Node("Router{0}".format(i+1), "emulab-xen")
        router.addService(PG.Install(url="http://pages.cs.wisc.edu/~rkrish/GENI/ospf-script-2intf.tar.gz", path="/local"))
        router.addService(PG.Execute(shell="sh", command="/local/ospf-script-2intf.sh".format(number)))
        router.exclusive = False
        router_intf_A = router.addInterface("if_RA{0}".format(i))
        router_intf_A.addAddress(PG.IPv4Address("192.166.{0}.2".format(i+1), "255.255.255.0"))
        router_intf_A_list.append(router_intf_A)
        router_intf_B = router.addInterface("if_RB{0}".format(i))
        router_intf_B.addAddress(PG.IPv4Address("192.167.{0}.2".format(i+1), "255.255.255.0"))
        router_intf_B_list.append(router_intf_B)
        r.addResource(router)

        hostHA = PG.Node("H{0}".format(2*i+1), "emulab-xen")
        hostHA.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
        hostHA.exclusive = False
        host_intf_A = hostHA.addInterface("if_HA{0}".format(i))
        host_intf_A.addAddress(PG.IPv4Address("192.165.{0}.2".format(i+1), "255.255.255.0"))
        host_intf_A_list.append(host_intf_A)
        r.addResource(hostHA)

        hostHB = PG.Node("H{0}".format(2*i+2), "emulab-xen")
        hostHB.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
        hostHB.exclusive = False
        host_intf_B = hostHB.addInterface("if_HB{0}".format(i))
        host_intf_B.addAddress(PG.IPv4Address("192.168.{0}.2".format(i+1), "255.255.255.0"))
        host_intf_B_list.append(host_intf_B)
        r.addResource(hostHB)

    for i in interfaces:
        linkHA = PG.Link("linkHA{0}".format(interfaces[i]))
        linkHA.addInterface(host_intf_A_list[i])
        linkHA.addInterface(nodeA_host_intf_list[i])
        linkHA.bandwidth = 20000
        r.addResource(linkHA)

        linkHB = PG.Link("linkHB{0}".format(interfaces[i]))
        linkHB.addInterface(host_intf_B_list[i])
        linkHB.addInterface(nodeB_host_intf_list[i])
        linkHB.bandwidth = 20000
        r.addResource(linkHB)

        linkRA = PG.Link("linkRA{0}".format(interfaces[i]))
        linkRA.addInterface(router_intf_A_list[i])
        linkRA.addInterface(nodeA_router_intf_list[i])
        linkRA.bandwidth = 20000
        r.addResource(linkRA)

        linkRB = PG.Link("linkRB{0}".format(interfaces[i]))
        linkRB.addInterface(router_intf_B_list[i])
        linkRB.addInterface(nodeB_router_intf_list[i])
        linkRB.bandwidth = 20000
        r.addResource(linkRB)

    name = "Performance-{0}.rspec".format(number)
    r.writeXML(name)

if __name__ == "__main__":
    logging.info("Did you run 'context-from-bundle --bundle ~/Downloads/omni.bundle' before this?\n")
    context = geni.util.loadContext()

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", help="Number of interfaces.", dest="number", type=int)
    args = parser.parse_args()

    nodes_rspec(context, args.number)
