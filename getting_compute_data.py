import requests
from datetime import datetime
from io import BytesIO
import json

from ssh_into_server import ssh_into_server

import matplotlib.pyplot as plt

command = "curl https://london.my-netdata.io/api/v1/data\?chart\=system.cpu\&after\=-600\&points\=20\&group\=average\&format\=json\&options\=seconds\&options\=jsonwrapServer%20response "


def unix_to_datetime(time):
    return datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

url = 'https://london.my-netdata.io/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'
url_ram = 'https://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20responsehttps://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'

def getting_netdata_data(url=url):
    data = json.loads(requests.get(url).text)
    print(data)
    return data

def plotting_cpu_vs_time(url=url):
    plt.clf()
    data = ssh_into_server('192.168.43.34','noob4u', 'abhi24783589', str(command))
    time = []
    cpu = []
    plt.xlabel('time') 
    plt.ylabel('cpu_usage') 
    plt.title('Cpu Usage v/s Time')
    for i in data['data']:
        time.append(i[0]) 
        cpu.append(i[7])
    
    buffer = BytesIO()
    plt.plot(time, cpu)
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer


def preparing_ram_graph_data(url=url):
    data = ssh_into_server('192.168.43.34','noob4u', 'abhi24783589', str(command))
    time = []
    free_ram = []
    used_ram = []
    cached_ram = []
    buffers_ram = []
    print(data)
    
    for i in data['data']:
        time.append(i[0]) 
        free_ram.append(i[1])
        used_ram.append(i[2])
        cached_ram.append(i[3])
        buffers_ram.append(i[4])
    
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
    plt.plot(x_object, y_object)
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer



