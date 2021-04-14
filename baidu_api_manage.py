#!/bin/env python

import json
import requests
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class BcloudManage(object):
    def __init__(self, url, headers, method="GET", data=dict()):
        from baidu_cloud_auth import Bcloud
        self.url = url
        self.headers = headers
        self.method = method
        self.data = data
        self.bcloud = Bcloud(url, headers, method)
        self.headers["authorization"] = self.bcloud.getAuthorization()
    
    def getData(self):
        return requests.get(self.url, headers=self.headers)

    def postData(self):
        return requests.post(self.url, headers=self.headers, data=json.dumps(self.data))

    def deleteData(self):
        return requests.delete(self.url, headers=self.headers, data=json.dumps(self.data))

    def putData(self):
        return requests.put(self.url, headers=self.headers, data=json.dumps(self.data))

    def mainData(self):
        typeData = {"GET": self.getData(), "POST": self.postData(), "DELETE": self.deleteData(), "PUT": self.putData()}
        return typeData[self.method]

class BcloudPassword(object):
    from baidu_base_config import Bcloud_AccessKeySecret

    @classmethod
    def encrypt(cls, password):
        if len(password) % 16 != 0:
            pendding = 16 - len(password) % 16
            password += chr(pendding) * (pendding)
        data = b2a_hex(AES.new(cls.Bcloud_AccessKeySecret[:16].encode('utf-8'), AES.MODE_ECB).encrypt(password.encode('utf-8')))
        return data.decode("utf-8")

    @classmethod
    def decrypt(cls, password):
        decrypted = AES.new(cls.Bcloud_AccessKeySecret[:16].encode('utf-8'), AES.MODE_ECB).decrypt(a2b_hex(password.encode('utf-8'))).decode('utf-8')
        pendding = ord(decrypted[len(decrypted) - 1])
        return decrypted[-pendding:]


if __name__ == "__main__":
    print("Baidu Cloud Api Class")
