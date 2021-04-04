from common.templates.Request import Request
from common.templates.Response import Response
from config import  *

class ShortConnectionHandler():
    def __init__(self,loggedInUser):
        self.loggedInUser = loggedInUser
        self.mapping = {
            "GET/login" : self._handle_get_login,
            "POST/login": self._handle_post_login,
            "GET/static": self._handle_get_static,
        }

    def _handle_get_login(self,request,conn):
        responseTemplate = Response()
        with open(TEMPLATE_PATH+"/loginPage.html", "r", encoding="UTF-8") as fp:
            data = fp.read()
        responseTemplate.data = data
        responseTemplate.sendHTML(conn)
        conn.close()

    def _handle_post_login(self,request,conn):
        data = request.data
        username = data.get("username")
        response = Response()
        if username in self.loggedInUser:
            response.data = {
                "status":0,
                "msg":"This username has been occupied."
            }
            response.sendAjax(conn)
            return
        response.setSession(username)
        response.headers["Connection"] = "Keep-Alive"
        return response



    def _handle_get_static(self,request,conn):
        pass

    def _handle_default(self,request,conn):
        rt = Response()
        rt.data = "404 not found"
        rt.send404(conn)
        conn.close()

    def handle(self,conn,request,loggedInUser=None):
        path = request.path
        method = request.method
        print(f"{method}  {path}")
        handlingFunc = self.mapping.get(method+path)
        if handlingFunc is None:
            self._handle_default(request,conn)
        else:
            res = handlingFunc(request,conn)
            return res



