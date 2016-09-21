__author__ = 'guorongxu'

import paramiko
from scp import SCPClient

## connecting the master instance of a cfncluster by the hostname, username and private key file
## return a ssh client
def connect_master(hostname, username, private_key_file):
    private_key = paramiko.RSAKey.from_private_key_file(private_key_file)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "connecting"
    ssh_client.connect(hostname=hostname, username=username, pkey=private_key)
    print "connected"

    return ssh_client

## executing command using the ssh client
def execute_command(ssh_client, command):
    print "Executing {}".format(command)
    stdin , stdout, stderr = ssh_client.exec_command(command)
    print stdout.read()
    print("--------")
    print stderr.read()

def copy_file(ssh_client, localpath, remotepath):
    # SCPCLient takes a paramiko transport as its only argument
    scp = SCPClient(ssh_client.get_transport())
    scp.put(localpath, remotepath)

## close the ssh connection
def close_connection(ssh_client):
    ssh_client.close()
