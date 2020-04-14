import re 
import requests

regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
      

def check_ip(Ip):  
    if(re.search(regex, Ip)):
        return True  
          
    return False

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

