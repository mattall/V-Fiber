'''
file for useful tools for various tests
'''
from paramiko import SSHClient, AutoAddPolicy

def do_ssh_and_send_command(username, address, password, server, command):
    port = 22
    c = SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    stdin, stdout, stderr = c.exec_command(command)
    print stdout.read(),
    c.close()

def get_ssh_connection(username, address, password):
    port = 22
    c = SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(AutoAddPolicy())
    c.connect(hostname = address, username = username, password = password)
    return c

if __name__=="__main__":
    pass
