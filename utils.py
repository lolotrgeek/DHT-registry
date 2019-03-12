from get_port import find_free_port
import socket
import os
import requests
import json

def getPublicAddress (): 
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify = True)
    if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit()
    data = response.json()
    print(data['ip'])
    return data['ip']

def getInternalAddress ():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    gateway = gw[2]
    host = socket.gethostname()
    print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
    return ipaddr

def getPort ():
    port = find_free_port()
    return port[0]


def removeDB(name):
    path = './'+ name
    try :
        os.rmdir(path)
    except : 
        print('Unable to remove: ' , name)