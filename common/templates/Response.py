import json
import base64
from config import *
from utils.DESCrypto import DESCrypto
class Response():


    def __init__(self):
        self.httpVersion = "HTTP/1.0"
        self.statusCode = "200 OK"
        self.headers = dict()
        self.data = ""

        self._crypto = DESCrypto(APP_SECRET)


    def _formulateResponse(self):
        self.headers["Content-Length"] = str(len(self.data))
        response = f"{self.httpVersion} {self.statusCode}\r\n"

        for k,v in self.headers.items():
            response += f"{k}: {v}\r\n"
        response += "\r\n"
        response = response.encode("UTF-8")

        if len(self.data) > 0:
            if self.headers.get("Content-Type") is not None and "image" in self.headers.get("Content-Type"):
                response += self.data
            else:
                response += self.data.encode("UTF-8")

        return response

    def setSession(self,string):
        byteArray = self._crypto.encrypt(string)
        encoded = base64.b64encode(byteArray)
        self.headers["Set-Cookie"] = f"session={encoded}; HttpOnly; Path=/"

    def sendHTML(self,conn):
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def send404(self,conn):
        self.statusCode = "404 Not Found"
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def sendAjax(self,conn):
        self.headers["Content-Type"] = "application/json"
        self.data = json.dumps(self.data)
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def sendRedirect(self,conn,location):
        self.statusCode = "301 Moved Permanently"
        self.headers["Location"] = location
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def sendJS(self,conn):
        self.headers["Content-Type"] = "application/javascript; charset=utf-8"
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def sendCSS(self,conn):
        self.headers["Content-Type"] = "text/css; charset=utf-8"
        byteStream = self._formulateResponse()
        conn.send(byteStream)

    def sendImage(self,conn,image_type):
        self.headers["Content-Type"] = f"image/{image_type}"
        byteStream = self._formulateResponse()
        conn.send(byteStream)


