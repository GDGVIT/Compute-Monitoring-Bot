import subprocess
import json
import asyncio


async def run_remote_commands_for_data(username, password, host, url_to_curl, port=22):
    command = "sshpass -p {}  ssh -p {}  -o StrictHostKeyChecking=no {}@{} 'curl -s {}'".format(password, port, username, host, url_to_curl)
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
    except Exception:
        return {"error": output}
    else:
        return {"error": str(error.decode("utf-8") )}


async def check_valid_ssh_and_netdata(username, password, host, port=22):
    url_to_curl = 'http://localhost:19999/api/v1/info'
    command = "sshpass -p {}  ssh -p {}  -o StrictHostKeyChecking=no {}@{} 'curl -s {}'".format(password, port, username, host, url_to_curl)
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
    except Exception:
        return {"error": error.decode('utf-8')}
    else:
        return {"error": str(error.decode("utf-8") )}

async def getting_info_by_command(username, password, host, command, port=22):
    command = "sshpass -p {}  ssh -p {}  -o StrictHostKeyChecking=no {}@{} '{}'".format(password, port, username, host, command)
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
            return {'error': error.decode("utf-8") }
    except Exception:
        return {"error": output.decode("utf-8") }
    else:
        return {"error": str(error.decode("utf-8"))}
