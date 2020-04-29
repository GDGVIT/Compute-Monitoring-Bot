from .getting_compute_data import plotting_and_returning_image, getting_netdata_data,unix_to_datetime
import matplotlib.pyplot as plt
from io import BytesIO

k="""
1)System Information
2)Virtual Memory Info
3)Boot Time
4)Cpu Info
5)Swap Memory
6)Disk Info
7)Network Info
"""


def image_for_various_parameters(param, ip_address):
    plt.clf()
    if param == 'System Information':
        print("No visual for system info")
        return False
    elif param == 'Cpu Info':
        url = 'http://{}:19999/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'.format(ip_address)
        data = getting_netdata_data(url)
        if not data:
            return data
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
    elif param == 'Boot Time':
        url = 'http://{}:19999/api/v1/data?chart=system.cpu&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'.format(ip_address)
        data = getting_netdata_data(url)
        if not data:
            return data
        time = []
        capacity = []
        plt.xlabel('Time') 
        plt.ylabel('Battery Percentage') 
        plt.title('Battery Percentage v/s Time')
        for i in data.get('data'):
            time.append(unix_to_datetime(i[0])) 
            capacity.append(i[1])
        
        buffer = BytesIO()
        plt.plot(time, capacity)
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return buffer
    elif param == 'Network Info':
        url = 'http://{}:19999/api/v1/data?chart=ipv4.packets&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'.format(ip_address)
        data = getting_netdata_data(url)
        if not data:
            return data
        time = []
        received = []
        sent = []
        forwarded = []
        delivered = []
        plt.xlabel('Time') 
        plt.ylabel('Network') 
        plt.title('Network v/s Time')
        for i in data.get('data'):
            time.append(unix_to_datetime(i[0])) 
            received.append(i[1])
            sent.append(i[2])
            forwarded.append(i[3])
            delivered.append(i[4])
        
        buffer = BytesIO()
        plt.plot(time, received)
        plt.plot(time, sent)
        plt.plot(time, forwarded)
        plt.plot(time, delivered)
        plt.savefig(buffer, format='png', dpi=80)
        buffer.seek(0)
        return buffer
    elif param == 'Virtual Memory Info':
        url = 'http://{}:19999/api/v1/data?chart=system.ram&after=-600&points=20&group=average&format=json&options=seconds&options=jsonwrapServer%20response'.format(ip_address)
        data = getting_netdata_data(url)
        if not data:
            return data
        time = []
        used_ram = []
        plt.xlabel('Time') 
        plt.ylabel('Virtual Memory') 
        plt.title('Virtual Memory v/s Time')
        for i in data.get('data'):
            time.append(unix_to_datetime(i[0])) 
            used_ram = [i[2]]
        
        buffer = BytesIO()
        plt.plot(time, used_ram)
        plt.savefig(buffer, format='png', dpi=80)
        buffer.seek(0)
        return buffer
    


