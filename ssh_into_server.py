import paramiko
import json


def ssh_into_server(hostname, username, password, cmd_to_execute):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to client")
    try:
        c.connect( hostname = hostname, username = username, password=password)
    except Exception as e:
        print("Unable to connect to the client")
        return {"error": "Connection could not be done!"}
    print( "Connected to Client")
    stdin , stdout, stderr = c.exec_command(cmd_to_execute)
    output = stdout.readlines()
    output = ' '.join(output)
    print("output is ", output)
    print( "Errors")
    print( stderr.read())
    c.close()
    if output:
        return output
    else:
        print(stderr)
        return {"error": stderr}



command = "curl http://localhost:19999/api/v1/data\?chart\=system.ram\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response "

