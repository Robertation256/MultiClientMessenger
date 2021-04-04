from config import Config

class StaticResourceController():
    def __init__(self):
        self.type = "short_connection"
        self.prefix = "static"

    def get_file(self,params):
        if not "name" in params:
            return None

        try:
            fileName, fileType = params["name"].split(".")
            path = Config.STATIC_FILE_PATH+"\\"+params["name"]

            if fileType == "js":
                with open(path,"r") as fp:
                    file = fp.read()
            elif fileType in ("jpg","png","jpeg"):
                with open(path,"rb") as fp:
                    file = fp.read()

        except:
            print("[Error in loading static file]")
