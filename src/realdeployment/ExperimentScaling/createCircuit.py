import geni.util
import logging
import geni.rspec.pg as PG
import argparse

def two_nodes_rspec(context, location1, location2, number):
    ''' Create an RSpec for a simple two-node link'''
    interfaces = [i for i in xrange(number)]
    r = PG.Request()

    stub = PG.Node("ig-%s" % (location1), "emulab-xen")
    stub.component_manager_id = "urn:publicid:IDN+instageni.wisc.edu+authority+cm"
    stub.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
    stub.exclusive = False
    stub_intf_list = []
    for i in interfaces:
        stub_intf = stub.addInterface("if{0}".format(i))
        stub_intf.addAddress(PG.IPv4Address("192.168.1.{0}".format(i+1), "255.255.255.0"))
        stub_intf_list.append(stub_intf)
    r.addResource(stub)

    real = PG.Node("ig-%s" % (location2), "emulab-xen")
    real.component_manager_id = "urn:publicid:IDN+instageni.rnet.missouri.edu+authority+cm"
    real.addService(PG.Execute(shell="sh", command="sudo yum install iperf -y"))
    real.exclusive = False
    real_intf_list = []
    for i in interfaces:
        real_intf = real.addInterface("if{0}".format(i))
        real_intf.addAddress(PG.IPv4Address("192.168.2.{0}".format(i+1), "255.255.255.0"))
        real_intf_list.append(real_intf)
    r.addResource(real)

    for i in interfaces:
        link = PG.Link("link{0}".format(interfaces[i]))
        link.addInterface(stub_intf_list[i])
        link.addInterface(real_intf_list[i])
        link.bandwidth = 20000
        r.addResource(link)

    name = "test-{0}-{1}-{2}.rspec".format(location1, location2, number)
    r.writeXML(name)

if __name__ == "__main__":
    logging.info("Did you run 'context-from-bundle --bundle ~/Downloads/omni.bundle' before this?\n")
    context = geni.util.loadContext()

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", help="Number of interfaces.", dest="number", type=int)
    args = parser.parse_args()

    two_nodes_rspec(context, "Wisconsin", "Missouri", args.number)
    # call("/Applications/omniTools-2.10/stitcher.app/Contents/MacOS/stitcher createsliver %s %s" % (args.slice, rspecName), shell=True)
