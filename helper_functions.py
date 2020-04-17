import re 
import requests
import json

regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
  

def check_ip(Ip):  
    if(re.search(regex, Ip)):
        return True  
          
    return False

def user_choice_for_monitoring_regex_check(choice):
    for i in str(choice):
        if i not in '1234567':
            return False 
    return True

def probe_server(ip_address):
    url = "http://{}:8000/check/health/".format(ip_address)
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
        return False
    if response.status_code == 200:
        return True
    return False

def making_a_cron_job(ip_address,params):
    url = "http://{}:8000/job/create/".format(ip_address)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    print(response.text)
    if response.status_code == 409:
        return ['error', 'Task by that name exists']
    elif response.status_code == 201:
        return ['success', 'Scheduled monitor successfully created']
    elif response.status_code == 400:
        return ['error', 'All parameters not set']
    else:
        return ['error', 'Unable to set a schedule successfully']

def deleting_a_cron_job(ip_address, name):
    url = "http://{}:8000/job/delete/".format(ip_address)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps({'name_of_job': name}), headers=headers)
    print(response.text)
    if response.status_code == 409:
        return ['error', 'No task by that name exists']
    elif response.status_code == 204:
        return ['success', 'Scheduled monitor successfully deleted']
    elif response.status_code == 500:
        return ['error', 'Unable to delete task']

def deleting_all_cron_jobs(ip_address):
    url = "http://{}:8000/job/delete/all/".format(ip_address)
    response = requests.post(url)
    print(response.text)
    if response.status_code == 204:
        return True
    else:
        return False


def getting_current_data_from_server(ip_address,metric):
    url_localhost = 'http://{}:8000/data/?metric={}'
    url = url_localhost.format(ip_address,metric)
    response = requests.get(url)
    output = json.loads(response.text)
    string = ""
    if metric == 'Cpu Info':
        string+= "This is a metric on your current CPU Info \n\n\n"
        for i in output:
            if i == 'Cores':
                string+="\n This part gives percentage usage of each core \n\n\n"
                for j in output[i]:
                    string+="{}: {}\n".format(j, output[i][j])

            else:
                string+="{}: {}\n".format(i, output[i])
    elif metric == 'Virtual Memory Info':
        string+= "This is a metric on your current Virtual Memory \n\n\n"
        for i in output:
            string+="{}: {}\n".format(i, output[i])
    elif metric == 'System Information':
        string+= "This is a baisc Info About your System \n\n\n"
        for i in output:
            string+="{}: {}\n".format(i, output[i])
    elif metric == 'Boot Time':
        string+= "This is a note of when your server was last restarted \n\n\n"
        string+= "The server was last booted on {}/{}/{} at {}:{}:{} GMT".format(
            output['day'],output['month'],output['year'], output['hour'], output['minute'],
            output['second']
        )
    elif metric == 'Swap Memory':
        string+= "This is a baisc Info About your Swap Memory \n\n\n"
        for i in output:
            string+="{}: {}\n".format(i, output[i])
    elif metric == 'Network Info':
        string+= "This is a baisc Info About your Network Info \n\n\n"
        for i in output:
            string+="{}: {}\n".format(i, output[i])
    elif metric == 'Disk Info':
        string = []
        string.append("This is a basic Info Regarding Your Disk Setup \n\n\n")
        string.append("\nThis is a list of the different disk partitions\n\n")
        for i in output:
            if i == 'Partitions':
                for j in output[i]:
                    string1 = ""
                    for k in output[i][j]:
                        if k == 'MountPoint':
                            string1+="MountPoint:  {}\n".format(output[i][j][k])
                        elif k == 'File System Type':
                            string1+= "File System Type {}\n".format(output[i][j][k])
                        elif k == 'Partition Usage':
                            string1+= "Partition Usage: \n"
                            string1+= "\tTotal Size: {}\n".format(output[i][j][k]['Total Size'])
                            string1+= "\tUsed: {}\n".format(output[i][j][k]['Used'])
                            string1+= "\tFree: {}\n".format(output[i][j][k]['Free'])
                            string1+= "\tPercentage: {}\n".format(output[i][j][k]['Percentage'])
                        string.append(string1)
            else:
                string.append("{}: {}".format(i, output[i]))
        
        print(len(string))


    return string