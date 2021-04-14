# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests

Bcloud_AccessKeyID="xxxxx"
Bcloud_AccessKeySecret="xxxxxx"

url = "http://xxxx.xxx.com" #apollo config url
data = requests.get(url)

if data.status_code == 200:
    print("Apollo Get Conf")
    Bcloud_AccessKeyID = data.json()["configurations"]["Bcloud_AccessKeyID"]
    Bcloud_AccessKeySecret = data.json()["configurations"]["Bcloud_AccessKeySecret"]
else:
    print("Apollo Error...")
