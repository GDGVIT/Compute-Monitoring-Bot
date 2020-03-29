import requests
import matplotlib.pyplot as plt 
from datetime import datetime
from io import BytesIO
import json

def unix_to_datetime(time):
    return datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

url = 'https://london.my-netdata.io/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'
url_ram = 'https://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20responsehttps://london.my-netdata.io/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'

def getting_netdata_data(url=url):
    data = json.loads(requests.get(url).text)
    print(data)
    return data

def plotting_cpu_vs_time(url=url):
    data = getting_netdata_data(url)
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


def plotting_ram_graph(url=url):
    data = getting_netdata_data(url_ram)
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
        
    plt.xlabel('time')
    plt.plot(time, free_ram, 'Free Ram')
    plt.plot(time, used_ram, 'Used Ram')
    plt.plot(time, cached_ram, 'Cached Ram')
    plt.plot(time, buffers_ram, 'Buffer Ram')
    
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

