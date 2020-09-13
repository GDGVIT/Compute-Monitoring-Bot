import subprocess
import json
import asyncio
from shlex import join, quote


async def run_remote_commands_for_data(username, password, host, url_to_curl, port='22'):
    command = "sshpass -p {} ssh -p {} -o StrictHostKeyChecking=no {}@{} 'curl -s {}'".format(quote(password), quote(port), quote(username), quote(host), quote(url_to_curl))
    # string = username + '@' + host
    # #command_1 = 'curl -s ' + url_to_curl
    # command = ["sshpass", "-p", password, "ssh", "-p", port, "-o", "StrictHostKeyChecking=no", string, '"curl', '-s', url_to_curl+'"']
    proc  = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )
    output, error = await proc.communicate()
    try:
        res = json.loads(output)
        return {"success":res}
    except Exception as e:
        print("This is error while parsing the output!")
        print(host," ",e, " ", error)
        return {"error": "We have some error in running some commands into your server, please check your creds once, or try checking netdata installation!"}
    else:
        print("This is error while executing!")
        print(host, " " ,error)
        return {"error": "Unable to execute this operation!"}

async def check_valid_ssh_and_netdata(username, password, host, port='22'):
    url_to_curl = 'http://localhost:19999/api/v1/info'
    command = "sshpass -p {} ssh -p {} -o StrictHostKeyChecking=no {}@{} 'curl -s {}'".format(quote(password), quote(str(port), quote(username), quote(host), quote(url_to_curl))
    # string = username + '@' + host
    # #command_1 = 'curl -s ' + url_to_curl
    # command = ["sshpass", "-p", password, "ssh", "-p", port, "-o", "StrictHostKeyChecking=no", string,'"curl', '-s', url_to_curl+'"']
    proc  = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )
    output, error = await proc.communicate()
    try:
        res = json.loads(output)
        if 'version' in res:
            return {"success":res}
        else:
            return {"error":'Netdata not installed or curl not installed, Install curl and run this on your vm to get started : bash<(curl -Ss https://my-netdata.io/kickstart.sh)'}
    except Exception as e:
        print(host, " ", e)
        return {"error": "Unable to validate server, please check creds and try again!"}
    else:
        print(host, " ", error)
        return {"error": "Unhandled error!"}

async def getting_info_by_command(username, password, host, command, port='22'):
    command = "sshpass -p {} ssh -p {}  -o StrictHostKeyChecking=no {}@{} {}".format(quote(password), quote(str(port)), quote(username), quote(host), quote(command))
    
    # string = username + '@' + host
    # command = ["sshpass", "-p", password, "ssh", "-p", port, "-o", "StrictHostKeyChecking=no", string].extend(shlex.split(command))
    
    proc  = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )
    output, error = await proc.communicate()
    try:
        if output:
            return {'success': output.decode("utf-8") }
        else:
            print(host, " ", error)
            return {'error':  "Error retrieving info!"}
    except Exception as e:
        print(host, " ", e)
        return {"error": "Unandled exception!" }
    else:
        print(host, " ", error)
        return {"error": "Unable to complete your request! Please try again"}
