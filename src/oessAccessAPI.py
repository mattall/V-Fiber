import requests
import requests.auth
import json
from base64 import b64encode
import warnings
warnings.filterwarnings("ignore")

class Workgroup(object):
    def __init__ (self, name, workgroup_id):
        self.workgroup_id = int(workgroup_id)
        self.name = name

    def __repr__ (self):
        return "[%d] %s" % (self.workgroup_id, self.name)

class Connection(object):
    BASE = "https://%s/oess/services/%s"

    def __init__ (self, hostname, uname, passwd):
        self.hostname = hostname
        self.url = Connection.BASE % (self.hostname, "data.cgi")
        self.purl = Connection.BASE % (self.hostname, "provisioning.cgi")
        self.auth = requests.auth.HTTPBasicAuth(uname, passwd)
        self.workgroup_id = None

    def setWorkgroupID (self, WID):
        self.workgroup_id = WID

    def setAuthInfo (self, uname, passwd):
        self.auth = requests.auth.HTTPBasicAuth(uname, passwd)

    def workgroups (self):
        r = requests.get(self.url, auth=self.auth, params={"action":"get_workgroups"}, verify=False)
        wgs = []
        for wg in r.json()["results"]:
            wgs.append(Workgroup(wg["name"], wg["workgroup_id"]))
        return wgs

    def get_workgroup_id (self, workgroup):
        r = requests.get(self.url, auth=self.auth, params={"action":"get_workgroups"}, verify=False)
        wgs = []
        for wg in r.json()["results"]:
            if workgroup == wg["name"]:
                self.setWorkgroupID(wg["workgroup_id"])
                return self.workgroup_id
        return ""

    def nodes (self):
        r = requests.get(self.url, auth=self.auth, params={"action":"get_all_node_status"})
        nl = []
        for nd in r.json()["results"]:
            nl.append(Node(nd))
        return nl

    def getPrimaryCircuits (self):
        r = requests.get(self.url, auth=self.auth, params={"action":"get_existing_circuits", "workgroup_id":self.workgroup_id}, verify=False)
        results = r.json()["results"]
        print results
        return results[0]["links"][0]

    def getNodeInterfaces (self, name):
        r = requests.get(self.url, auth=self.auth, params={"action":"get_node_interfaces", "workgroup_id":self.workgroup_id, "node":name}, verify=False)
        return r.json()["results"]

    def provisionVLANPatch (self, desc, node_name, links, backupLinks, intf_a_name):

        payload = {"action" : "provision_circuit", "workgroup_id" : self.workgroup_id, \
               "circuit_id" : -1, "description" : desc, "bandwidth" : 0, "provision_time": -1, \
               "remove_time" : -1, "link" : [], "backup_link" : [], "remote_nodes" : [], \
               "remote_tags" : [], "restore_to_primary" : 0, "node" : [], "interface" : [], \
               "tag" : []}

        payload["node"].extend(node_name)
        payload["link"].extend(links)
        payload["backup_link"].extend(backupLinks)
        payload["interface"].extend(intf_a_name)
        # payload["tag"].extend(tag)

        # payload["node"].append(node_name)
        # payload["interface"].append(intf_b_name)
        # payload["tag"].append(tag)

        r = requests.get(self.purl, auth=self.auth, data = payload, verify=False)
        return r.json()

if __name__ == "__main__":
    '''
    #######################################################
    #VM credentials
    #######################################################
    # OESS auth : meena/oess
    # Machine shell : oess/oess
    # Machine su password : oessadmin
    # mysql: root / oess and oess / oess
    # http: oess-test / changeme
    #######################################################
    '''
    workgroup_name = "user"
    conn = Connection("192.168.56.103","meena","oess")
    for c in conn.workgroups():
        print c
    workgroupID = conn.get_workgroup_id(workgroup_name)
    conn.setWorkgroupID(workgroupID)
    print "Required workgroup ID is: " + str(workgroupID)

    primaryCircuit = conn.getPrimaryCircuits()
    print primaryCircuit["node_z"], primaryCircuit["interface_z"]
    print primaryCircuit["node_a"], primaryCircuit["interface_a"]
    print primaryCircuit["name"]

    provisionResult = conn.provisionVLANPatch("Simple circuit attempt", \
                                              [primaryCircuit["node_a"], primaryCircuit["node_z"]], \
                                              [primaryCircuit["name"]], \
                                              ["s3NYeth2--s2Chicagoeth1","s4Atlantaeth2--s2Chicagoeth2","s4Atlantaeth1--s2Chicagoeth2"],\
                                              [primaryCircuit["interface_a"], primaryCircuit["interface_z"]] \
                                            )
    print provisionResult

    primaryCircuit = conn.getPrimaryCircuits()
    print primaryCircuit["node_z"], primaryCircuit["interface_z"]
    print primaryCircuit["node_a"], primaryCircuit["interface_a"]
    print primaryCircuit["name"]
