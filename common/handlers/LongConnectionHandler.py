from config import Config
from common.templates.Request import Request
from common.templates.Response import Response

class LongConnectionHandler:

    def __init__(self):
        self.mapping = {
            "GET/refresh": self.handle_refresh,
            "GET/chatroom": self.handle_get_chatroom
        }

    def dispatch(self, request, conn):
        path = request.path
        method = request.method
        handlingFunc = self.mapping.get(method + path)
        if handlingFunc is None:
            self._handle_default(request, conn)
        else:
            handlingFunc(request, conn)

    def handle_get_chatroom(self,request,conn):
        with open(Config.TEMPLATE_PATH+"\\chatroom.html","r") as fp:
            data = fp.read()
        response = Response()
        response.data = data
        response.sendHTML(conn)

    def handle_refresh(self,request,conn):
        pass




    def _handle_default(self,request,conn):
        rt = Response()
        rt.data = {
            "status":0,
            "msg":"Resource not found"
        }
        rt.sendAjax(conn)


    def handle(self,user):
        while True:
            data = user.conn.recv(1024)
            if len(data)>0:
                request = Request.getRequest(data)
                print(f"[Long connection handler] {request.method}  {request.path}")
                self.dispatch(request,user.conn)



