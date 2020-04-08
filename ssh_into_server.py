import paramiko
import json


def ssh_into_server(hostname, username, password, cmd_to_execute):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to client")
    c.connect( hostname = hostname, username = username, password=password, port=22)
    print( "Connected to Client")
    stdin , stdout, stderr = c.exec_command(cmd_to_execute)
    output = stdout.readlines()
    output = ' '.join(output)
    print("output is ", output)
    print( "Errors")
    print( stderr.read())
    c.close()
    return output




command = "curl http://localhost:19999/api/v1/data\?chart\=system.ram\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response "

