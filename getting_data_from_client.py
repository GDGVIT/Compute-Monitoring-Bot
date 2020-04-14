import requests
import json



def get_available_choices_to_monitor():
    response = requests.get("http://0.0.0.0:8000/choices/")
    #print(response.text)
    choices = json.loads(response.text)
    str = """These are the following available choices that you can monitor :\n"""
    count = 1
    for i in choices['choice']:
        str += "{})  {}\n".format(count,i)
        count+=1
    return str

def get_available_choices_to_monitor_list():
    response = requests.get("http://0.0.0.0:8000/choices/")
    #print(response.text)
    choices = json.loads(response.text)
    return choices['choice']


def respond_to_server_request(metric):
    response = requests.get("http://0.0.0.0:8000/data/?metric={}".format(metric))
    return str(response.text)

def getting_monitoring_data_for_different_params(metric):
    response = requests.get("http://0.0.0.0:8000/data/?metric={}".format(metric))
    # if 'Partitions' in response.data:
    #     pass
    

