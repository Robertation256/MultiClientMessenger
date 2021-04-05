from common.templates.Response import Response
from dto.User import User
import threading
from config import *

class ShortConnectionHandler():
    def __init__(self,loggedInUser,loggedInUserThreads,longConnectionHandler):
        self.loggedInUsers = loggedInUser
        self.loggedInUserThreads = loggedInUserThreads
        self.longConnectionHandler = longConnectionHandler
        self.mapping = {
            "GET/login" : self._handle_get_login,
            "POST/login": self._handle_post_login,
            "GET/chatroom": self._handle_get_chatroom,
            "GET/static": self._handle_get_static,
            "GET/connect": self._handle_establish_long_connection
        }

    def _handle_get_login(self,request,conn):
        responseTemplate = Response()
        with open(TEMPLATE_PATH+"/loginPage.html", "r", encoding="UTF-8") as fp:
            data = fp.read()
        responseTemplate.data = data
        responseTemplate.sendHTML(conn)

    def _handle_post_login(self,request,conn):
        data = request.data
        username = data.get("username")
        response = Response()
        if username in self.loggedInUsers:
            response.data = {
                "status":0,
                "msg":"This username has been occupied."
            }
            response.sendAjax(conn)
            return
        avatar_id = data["avatar_id"]
        user = User(
            name=username,
            avatar_id=avatar_id,
            conn=conn,
        )
        self.loggedInUsers[username] = user
        response.setSession(username)
        response.sendRedirect(conn,location="/chatroom")

    def _handle_get_chatroom(self,request,conn):
        with open(TEMPLATE_PATH+"\\chatroom.html","r") as fp:
            data = fp.read()
        response = Response()
        response.data = data
        response.sendHTML(conn)

    def _handle_get_static(self,request,conn):
        params = request.params
        if "file_name" not in params:
            self._handle_default(request,conn)

        file_name = params.get("file_name")

        try:
            file_type = file_name.split(".")
            if file_type == "js":
                with open(STATIC_FILE_PATH+"/js/"+file_name,"r") as fp:
                    file = fp.read()
                response = Response()
                response.data = file
                response.sendJS(conn)

            elif file_type == "css":
                with open(STATIC_FILE_PATH+"/css/"+file_name,"r") as fp:
                    file = fp.read()
                response = Response()
                response.data = file
                response.sendCSS(conn)


            elif file_type in ["jpg",'png','jpeg']:
                with open(STATIC_FILE_PATH + "/image/" + file_name, "r") as fp:
                    file = fp.read()
                response = Response()
                response.data = file
                response.sendImage(conn,file_type)
            else:
                self._handle_default(request,conn)
        except:
            print(f"[File not found] {file_name}")
            self._handle_default(request,conn)

    def _handle_establish_long_connection(self,request,conn):
        username = request.getSession()
        if username in self.loggedInUsers and self.loggedInUsers[username].first_time_request:
            thread = threading.Thread(target=self.longConnectionHandler.handle,args=(self.loggedInUsers[username],))
            self.loggedInUserThreads[username] = thread
            thread.start()
            response = Response()
            response.data = {
                "status":1,
                "msg":"connection established"
            }
            response.headers["Connection"] = "Keep-Alive"
            response.sendAjax(conn)
            return "Don't close"
        else:
            self._handle_default(request,conn)


    def _handle_default(self,request,conn):
        rt = Response()
        rt.data = "404 not found"
        rt.send404(conn)

    def handle(self,conn,request):
        path = request.path
        method = request.method
        print(f"{method}  {path}")
        handlingFunc = self.mapping.get(method+path)

        if handlingFunc is None:
            res = self._handle_default(request,conn)
        else:
            res = handlingFunc(request,conn)

        if res != "Don't close":
            conn.close()



