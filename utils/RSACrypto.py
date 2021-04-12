import rsa
import base64
from config import *

class RSACrypto():
    def __init__(self):
        self._private_key = rsa.PrivateKey.load_pkcs1(PRIVATE_KEY.encode("utf-8"))


    def decrypt(self,string):
        try:
            return rsa.decrypt(base64.b64decode(string),self._private_key).decode("utf-8")
        except:
            return None