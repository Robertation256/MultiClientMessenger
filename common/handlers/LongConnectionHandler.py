from common.templates.Request import Request
from common.templates.Response import Response

class LongConnectionHandler:

    def __init__(self,
                 chatGroupId2username,
                 username2chatGroupId,
                 history_message
    ):
        self.chatGroupId2username = chatGroupId2username
        self.username2chatGroupId = username2chatGroupId
        self.history_message = history_message
        self.mapping = {
            "GET/refresh": self._handle_refresh,
            "GET/join": self._handle_join,
            "GET/send_message": self._handle_send_message
        }

    def dispatch(self, request, conn):
        path = request.path
        method = request.method
        handlingFunc = self.mapping.get(method + path)
        if handlingFunc is None:
            self._handle_default(request, conn)
        else:
            handlingFunc(request, conn)


    def _handle_refresh(self,request,conn):
        pass

    def _handle_join(self,request,conn):
        pass

    def _handle_send_message(self,request,conn):
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



