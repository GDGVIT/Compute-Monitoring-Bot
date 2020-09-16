import requests
from datetime import datetime
from io import BytesIO
import json

from .ssh_into_server import ssh_into_server

import matplotlib.pyplot as plt

cpu_command = "curl http://localhost:19999/api/v1/data\?chart\=system.cpu\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response"
ram_command = "curl http://localhost:19999/api/v1/data\?chart\=system.ram\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response"

def unix_to_datetime(time):
    return datetime.utcfromtimestamp(int(time)).strftime('%H:%M')

url = 'https://london.my-netdata.io/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'
url_ram = 'https://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20responsehttps://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'

def getting_netdata_data(url=url):
    try:
        data = json.loads(requests.get(url).text)
        print(data)
        return data
    except Exception as e:
        print(e)
        return False

def plotting_cpu_vs_time(host, username, password):
    plt.clf()
    data = json.loads(ssh_into_server(host, username, password, str(cpu_command)))
    if 'error' in data:
        return False
    print("data in cpu plot receive is ", data)
    print(type(data))
    time = []
    cpu = []
    plt.xlabel('time') 
    plt.ylabel('cpu_usage') 
    plt.title('Cpu Usage v/s Time')
    for i in data.get('data'):
        time.append(unix_to_datetime(i[0])) 
        cpu.append(i[7])
    
    buffer = BytesIO()
    plt.plot(time, cpu)
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer


def plotting_cpu_vs_time_without_ssh(ip_address):
    plt.clf()
    response = requests.get('http://{}:19999/api/v1/data?chart=cpu.cpu0&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'.format(ip_address))
    
    if response.status_code == 200:
        data = json.loads(response.text)
    else:
        print(response.status_code)
        return False
    
    print("Data in cpu plot receive is ", data)
    print(type(data))
    time = []
    cpu = []
    plt.xlabel('time') 
    plt.ylabel('cpu_usage') 
    plt.title('Cpu Usage v/s Time')
    for i in data.get('data'):
        time.append(unix_to_datetime(i[0])) 
        cpu.append(i[7])
    
    buffer = BytesIO()
    plt.plot(time, cpu)
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer


def preparing_ram_graph_data(host, username, password):
    data = json.loads(ssh_into_server(host, username, password, str(ram_command)))
    time = []
    free_ram = []
    used_ram = []
    cached_ram = []
    buffers_ram = []
    print(data)
    
    for i in data.get('data'):
        time.append(unix_to_datetime(i[0]))
        free_ram.append(i[1])
        used_ram.append(i[2])
        cached_ram.append(i[3])
        buffers_ram.append(i[4])
    print(time)
    return {
        'free_ram': free_ram,
        'used_ram': used_ram,
        'cached_ram': cached_ram,
        'buffers_ram': buffers_ram,
        'time': time
    }  


def plotting_and_returning_image(x_object, y_object, y_label, x_label):
    plt.clf()
    plt.xlabel(x_label) 
    plt.ylabel(y_label) 
    plt.title('{} v/s {}'.format(y_label, x_label))
    
    buffer = BytesIO()
    #plt.figure(figsize=(30,20))
    plt.plot(x_object, y_object)
    plt.savefig(buffer, format='png',dpi=80)
    buffer.seek(0)
    return buffer




