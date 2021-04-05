from urllib.parse import parse_qs
from utils.DESCrypto import DESCrypto
from config import *
import base64

class Request():

    def __init__(self):
        self._crypto = DESCrypto(APP_SECRET)
        self.headers = dict()
        self.params = dict()
        self.method = None
        self.path = None
        self.httpVersion = None
        self.data = None



    def getSession(self):
        sessionStr = self.headers.get("Cookie")
        if sessionStr is None:
            return None

        base64Encoded = sessionStr.split("=")[1]
        byteArray = base64.b16decode(base64Encoded)
        username = self._crypto.decrypt(byteArray)
        return username



    @staticmethod
    def getRequest(byteStream):
        '''

        :param byteStream:
        :return: Request Object
        '''
        try:
            data = byteStream.decode("UTF-8")
        except:
            print("[ByteStream decoding failure]")
            return None

        returnInstance = Request()

        httpWords = data.split("\r\n")

        try:
            requestFields = httpWords[0].split(" ")
            returnInstance.method = requestFields[0]
            returnInstance.path = requestFields[1]
            returnInstance.httpVersion = requestFields[2]
        except:
            print("[Request fields decoding failure]")
            print(httpWords)
            return None

        lineNum = 1
        while lineNum < len(httpWords) and len(httpWords[lineNum]) > 0:
            try:
                headerType, value = httpWords[lineNum].split(":")
                returnInstance.headers[headerType] = value
            except:
                pass
            lineNum += 1

        lineNum += 1

        #handle form data
        if "Content-Type" in returnInstance.headers and lineNum < len(httpWords):
            if returnInstance.headers["Content-Type"].strip(" ") == "application/x-www-form-urlencoded":
                data = parse_qs(httpWords[lineNum])
                for k,v in data.items():
                    if len(v) == 1:
                        data[k] = v[0]
                returnInstance.data=data

        #handle url params
        if returnInstance.path is not None:
            urlSegs = returnInstance.path.split("?")
            if len(urlSegs)>1:
                params = parse_qs(urlSegs[1])
                for k, v in params:
                    if len(v) == 1:
                        returnInstance.params[k] = v[0]
                    else:
                        returnInstance.params[k] = v
        
        returnInstance.path = returnInstance.path.split("?")[0]

        return returnInstance





