from telegram import ReplyKeyboardMarkup
import matplotlib.pyplot as plt
from io import BytesIO

from .ssh_via_subprocess import (
    run_remote_commands_for_data
)
import asyncio
from datetime import datetime

CHOOSING, TYPING_REPLY, TYPING_CHOICE, DONE, CANCEL = range(5)
CHOOSING_BOT_PARAMS, BOT_REPLY, BOT_ADDITIONAL_OPTIONS, ADD_ONS, CHOOSING_SCHEDULER_PARAMS, TYPING_SCHEDULER_CHOICE, TYPING_SCHEDULER_REPLY  = range(7)


monitor_reply_keyboard = [['System Information','Virtual Memory Info'],['Boot Time','Cpu Info','Swap Memory'],
['Disk Info','Network Info'], ['Exit', 'Done']]

monitor_choices = ['System Information','Virtual Memory Info','Boot Time','Cpu Info','Swap Memory','Disk Info','Network Info']
monitor_markup = ReplyKeyboardMarkup(monitor_reply_keyboard, one_time_keyboard=True)

reply_keyboard_for_ssh_setup = [['Username', 'Password', 'Ip Address', 'Port'],
                  ['Cancel', 'Done']]
markup_for_ssh_setup = ReplyKeyboardMarkup(reply_keyboard_for_ssh_setup, one_time_keyboard=True)


default_commands = [
    "curl http://localhost:19999/api/v1/data?chart=system.cpu",
    "curl http://localhost:19999/api/v1/data?chart=system.ram"
    ]

def unix_to_datetime(time):
    return datetime.utcfromtimestamp(int(time)).strftime('%H:%M')


def image_for_monitoring(param, username, password, host, port=22, data=None):
    plt.clf()
    if data:
        if param == 'System Information':
            print("No visual for system info")
            return {'error': "No visual for system info"}
        elif param == 'Cpu Info':
            try:
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
                
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}
        
        elif param == 'Boot Time':
            try:
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}

        elif param == 'Network Info':
            try:
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}

        elif param == 'Virtual Memory Info':
            try:
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
                time = []
                used_ram = []
                plt.xlabel('Time') 
                plt.ylabel('Virtual Memory') 
                plt.title('Virtual Memory v/s Time')
                for i in data.get('data'):
                    time.append(unix_to_datetime(i[0])) 
                    used_ram.append(i[2])
                
                buffer = BytesIO()
                plt.plot(time, used_ram)
                plt.savefig(buffer, format='png', dpi=80)
                buffer.seek(0)
                return {'success': buffer}
            except Exception as e:
                return {'error': e}
    else:
        if param == 'System Information':
            print("No visual for system info")
            return {'error': "No visual for system info"}
        elif param == 'Cpu Info':
            try:
                url = 'http://localhost:19999/api/v1/data?chart=system.cpu'
                data = asyncio.run(run_remote_commands_for_data(username, password, host, url, port))
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}
        
        elif param == 'Boot Time':
            try:
                url = 'http://localhost:19999/api/v1/data?chart=powersupply_capacity.BAT1'
                data = asyncio.run(run_remote_commands_for_data(username, password, host, url, port))
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}

        elif param == 'Network Info':
            try:
                url = 'http://localhost:19999/api/v1/data?chart=ipv4.packets'
                data = asyncio.run(run_remote_commands_for_data(username, password, host, url, port))
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
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
                return {'success': buffer}
            except Exception as e:
                return {'error': e}

        elif param == 'Virtual Memory Info':
            try:
                url = 'http://localhost:19999/api/v1/data?chart=system.ram'
                data = asyncio.run(run_remote_commands_for_data(username, password, host, url, port))
                if 'error' in data:
                    return {'error': str(data)}
                else:
                    data = data['success']
                time = []
                used_ram = []
                plt.xlabel('Time') 
                plt.ylabel('Virtual Memory') 
                plt.title('Virtual Memory v/s Time')
                for i in data.get('data'):
                    time.append(unix_to_datetime(i[0])) 
                    used_ram.append(i[2])
                
                buffer = BytesIO()
                plt.plot(time, used_ram)
                plt.savefig(buffer, format='png', dpi=80)
                buffer.seek(0)
                return {'success': buffer}
            except Exception as e:
                return {'error': e}
        else:
            print("No visual for any other type {}".format(param))
            return {'error': "No visual for system info"}
def metric_to_command(metric, password):
    if metric == 'Cpu Info':
        return 'ps -eo user,pid,%cpu,%mem,time k-pcpu --no-headers| head -6'
    elif metric == 'Virtual Memory Info':
        return 'cat /proc/meminfo | head -6'
    elif metric == 'Network Info':
        return 'curl ifconfig.me'
    elif metric == 'System Information':
        return 'echo {} | sudo -S lshw'.format(password)
    elif metric == 'Boot Time':
        return 'uptime'
    elif metric == 'Disk Info':
        return 'df -h --output=source,fstype,size,used,avail,pcent,target -x tmpfs -x devtmpfs'
    elif metric == 'Swap Memory':
        return 'grep Swap /proc/meminfo'

def info_for_monitoring(metric, data):
    output = data
    strings = []
    string = ""
    if metric == 'Cpu Info':
        strings.append("This is a metric on your current CPU Info \n")
        data = data.split('\n')
        data = data[:len(data)-2]
        data = [l.split() for l in data]
        for j in range(len(data)):
            string = "User : {}\npid: {}\nCpu%: {}\nMem%: {}\nTime: {}".format(data[j][0], data[j][1], data[j][2], data[j][3], data[j][4])
            strings.append(string)
    elif metric == 'Virtual Memory Info':
        strings.append("This is a metric on Virtual Memory Info \n")
        strings.append(data)
    elif metric == 'System Information':
        strings.append("This is a basic Info About your System \n")
        data = data.split('*')
        strings.extend(data)
    elif metric == 'Boot Time':
        strings.append("This is a note of uptime of your server \n")
        strings.append(str(data))
    elif metric == 'Swap Memory':
        strings.append("This is a basic info about your Swap Memory \n")
        strings.append(data)
    elif metric == 'Network Info':
        strings.append("This is a basic info about your Network Info \n")
        strings.append("Please note this is the public ip address of your system, feel free to make prs and make this info verbose")
        strings.append(data)
    elif metric == 'Disk Info':
        strings.append("This is an info about your disks \n")
        strings.append("Please note that the data is in the order of source, filesystemtype,size,used,available,percentage,target")
        data = data.split('\n')[1:]
        strings.extend(data)
    return strings

def initialize_variables_for_bot(update, context):
    user_data = context.user_data
    user_data['monitor'] = {}
    user_data['monitor']['state'] = 'initial'
    user_data['monitor']['user_response'] = ''
    user_data['monitor']['monitor_variables'] = []
    user_data['monitor']['add_ons'] = []
    user_data['monitor']['notifications_set'] = {}
    user_data['monitor']['schedule_monitoring'] = False


## Testing

# def virtual_memory_plot():
#     plt.clf()
#     try:
#         url = 'http://localhost:19999/api/v1/data?chart=powersupply_capacity.BAT1'
#         #data = run_remote_commands_for_data(username, password, host, url_to_curl, port)['success']
#         data = asyncio.run(run_remote_commands_for_data('kali', 'L04DB4L4NC3R_4U', '2.tcp.ngrok.io', url, 14190))
#         if 'error' in data:
#             return {'error': str(data)}
#         else:
#             data = data['success']
        
#         time = []
#         capacity = []
#         plt.xlabel('Time') 
#         plt.ylabel('Battery Percentage') 
#         plt.title('Battery Percentage v/s Time')
#         for i in data.get('data'):
#             time.append(unix_to_datetime(i[0])) 
#             capacity.append(i[1])
        
#         buffer = BytesIO()
#         plt.plot(time, capacity)
#         plt.savefig(buffer, format='png')
#         buffer.seek(0)
#         return {'success': buffer}
#     except Exception as e:
#         return {'error': e}