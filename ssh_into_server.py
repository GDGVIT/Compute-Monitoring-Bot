import paramiko
import json


def ssh_into_server(hostname, username, password, cmd_to_execute):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting")
    c.connect( hostname = hostname, username = username, password=password)
    print( "connected")
    stdin , stdout, stderr = c.exec_command(cmd_to_execute)
    output = stdout.readlines()
    output = ' '.join(output)
    output = json.loads(output)
    print( "Errors")
    print( stderr.read())
    c.close()
    return output




command = "curl https://london.my-netdata.io/api/v1/data\?chart\=system.cpu\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response "

#ssh_into_server('192.168.43.34','noob4u', 'abhi24783589', str(command))