import requests
import matplotlib.pyplot as plt 
from datetime import datetime
from io import BytesIO
import json

def unix_to_datetime(time):
    return datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

url = 'https://london.my-netdata.io/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'

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
