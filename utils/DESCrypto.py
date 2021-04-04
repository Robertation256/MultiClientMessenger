from pyDes import des, CBC, PAD_PKCS5


class DESCrypto:

    def __init__(self, secret_key):
        self._secret_key = secret_key
        self._crypto = des(self._secret_key, CBC, "\0\0\0\0\0\0\0\0" ,padmode=PAD_PKCS5)

    def encrypt(self,string):
        byteArray = string.encode("UTF-8")
        return self._crypto.encrypt(byteArray)


    def decrypt(self,byteArray):
        try:
            return self._crypto.decrypt(byteArray)
        except:
            return "Unknown charset"


if __name__ == "__main__":
    c = DESCrypto("DESCRYPT")
    res = c.encrypt("你好呀")
    print(res)
    print(c.decrypt(res).decode("UTF-8"))





