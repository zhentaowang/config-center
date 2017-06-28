# -*- coding: utf-8 -*-
import time
import os
import pycurl as pycurl
from tornado.options import options
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import json
import StringIO

Permission = {
    'WRITE': 'w_',
    'READ': 'r_',
    'UPDATE': 'u_',
    'DELETE': 'd_',
    'APP_ALL': 'app_all'
}


def load_properties():
    if os.path.exists('/etc/confcenter-api.conf'):
        options.parse_config_file('/etc/confcenter-api.conf')
    elif os.path.exists('/code/confcenter.conf'):
        options.parse_config_file('/code/confcenter.conf')
    elif os.path.exists('./confcenter.conf'):
        options.parse_config_file('./confcenter.conf')
    options.parse_command_line()


load_properties()


def get_property(property):
    return options[property]


def joinPath(split, arrStr):
    result = ''
    flat = False
    for str in arrStr:
        if flat:
            result += split
        result += str
        flat = True
    return result


def version():
    t = time.time()
    return time.strftime("%Y%m%d%H%M%S", time.localtime(t))


def padding(text):
    add = 16 - len(text) % 16
    text += add * '\0'
    return text


sys_secret_key = '12345678123456'


def encrypt(plaintext, secret_key=sys_secret_key):
    plaintext = padding(plaintext)
    secret_key = padding(secret_key)
    aes = AES.new(secret_key, AES.MODE_CBC, secret_key)
    return b2a_hex(aes.encrypt(plaintext))


def decrypt(ciphertext, secret_key=sys_secret_key):
    secret_key = padding(secret_key)
    aes = AES.new(secret_key, AES.MODE_CBC, secret_key)
    plaintext = aes.decrypt(a2b_hex(ciphertext))
    return plaintext.rstrip('\0')


def auth(access_token, permission):
    if access_token is None:
        return False
    c = pycurl.Curl()
    c.setopt(pycurl.URL,
             get_property(
                 'auth_server') + '/user/permission?access_token=' + access_token + "&permission=" + permission)
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    json_str = str(b.getvalue())
    obj = json.loads(json_str)
    if 'allowed' not in obj:
        return False
    return obj['allowed']
