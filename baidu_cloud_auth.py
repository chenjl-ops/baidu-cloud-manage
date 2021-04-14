# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Bcloud(object):
    def __init__(self, url, headers, method="GET"):
        self.url = url
        self.headers = headers
        self.method = method.upper()
        self.sign_headers = {"host", "content-md5", "content-length", "content-type"}


    def getAuthorization(self):
        from baseConf import Bcloud_AccessKeyID
        return "bce-auth-v1/{key}/{utc}/1800/{header}/{signature}".format(key=Bcloud_AccessKeyID, utc=self.getUtcTime(), header=self.getSignedHeaders() , signature=self.getSignature())

    def getSignature(self):
        return self.getHmacSha256(self.__getSigningKey(), self.getCanonicalRequest())

    def getCanonicalRequest(self): #uri, query, headers
        CanonicalUri = self.__getCanonicalURI()
        CanonicalQueryString = self.__getCanonicalQueryString()
        CanonicalHeaders = self.__getCanonicalHeaders()
        data = "{method}\n{CanonicalURI}\n{CanonicalQueryString}\n{CanonicalHeaders}".format(method=self.method, CanonicalURI=CanonicalUri, CanonicalQueryString=CanonicalQueryString, CanonicalHeaders=CanonicalHeaders)
        return data
    
    def __getCanonicalURI(self):
        urlParse = self.getUrlParse()
        if urlParse.path:
            return self.getEncode(urlParse.path)
        else:
            return self.getEncode("/")

    def __getCanonicalQueryString(self):
        urlParse = self.getUrlParse()
        if urlParse.query:
            query = urlParse.query.split("&")
            data = list()
            for i in query:
                s = i.split("=")
                if len(s) < 2 and len(s) != 0:
                    data.append("%s="%self.getEncode(s[0]))
                else:
                    data.append("%s=%s"%(self.getEncode(s[0]), self.getEncode(s[1])))
            data.sort()
            return "&".join(data)
        else:
            return ""

    def __getCanonicalHeaders(self):
        data = list()
        #sign_headers = {"host", "content-md5", "content-length", "content-type", "date"}
        for k, v in self.headers.items():
            if k.startswith("x-bce-") or k.lower() in self.sign_headers:
                data.append("%s:%s"%(self.getEncode(k.lower()), self.getEncode(str(v).strip())))
        data.sort()
        return "\n".join(data)

    def getSignedHeaders(self):
        data = [i.lower() for i in list(self.headers.keys()) if i.startswith("x-bce-") or i.lower() in self.sign_headers]
        data.sort()
        return ";".join(data)

    def getUrlParse(self):
        import urllib, urllib.request
        return urllib.parse.urlsplit(self.url)

    def getEncode(self, s):
        import urllib, urllib.request
        return urllib.parse.quote(s)

    def getSha256(self, s):
        import hashlib
        S = hashlib.sha256()
        S.update(s.encode("utf-8"))
        return S.hexdigest()

    def __getSigningKey(self):
        from baidu_base_config import Bcloud_AccessKeyID, Bcloud_AccessKeySecret
        AuthStringPrefix = "bce-auth-v1/{accessKeyId}/{timestamp}/{expirationPeriodInSeconds}".format(accessKeyId=Bcloud_AccessKeyID, timestamp=self.getUtcTime(), expirationPeriodInSeconds=1800)
        return self.getHmacSha256(Bcloud_AccessKeySecret, AuthStringPrefix)

    def getHmacSha256(self, k, s): 
        import hmac, hashlib
        S = hmac.new(k.encode("utf-8"), s.encode("utf-8"), digestmod=hashlib.sha256)
        return S.hexdigest()

    def getUtcTime(self, timestamp=0):
        import datetime
        if timestamp == 0:
            utctime = datetime.datetime.utcnow()
        else:
            utctime = datetime.datetime.utcfromtimestamp(timestamp)

        return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (
            utctime.year, utctime.month, utctime.day,
            utctime.hour, utctime.minute, utctime.second)
