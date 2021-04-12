from pyDes import triple_des, CBC, PAD_PKCS5
import base64

class DESCrypto:

    def __init__(self, secret_key):
        self._secret_key = secret_key
        self._crypto = triple_des(self._secret_key, padmode=PAD_PKCS5)

    # string to b64 string
    def encrypt(self,string):
        byte_array = string.encode("UTF-8")
        encrypted = self._crypto.encrypt(byte_array)
        return base64.b64encode(encrypted).decode()

    # b64 string to string
    def decrypt(self,base64_string):
        try:
            byteArray = base64.b64decode(base64_string)
            return self._crypto.decrypt(byteArray).decode()
        except:
            return None



