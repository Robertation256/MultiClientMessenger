from common.templates.Response import Response
from common.templates.Request import Request
from dto.User import User
from utils.RSACrypto import RSACrypto
from utils.DESCrypto import DESCrypto
import threading
import time
import uuid
from config import *

class ShortConnectionHandler():
    def __init__(
            self,
            loggedInUser,
            longConnectionHandler,
            chatGroupId2username,
            username2chatGroupId
    ):
        self.loggedInUsers = loggedInUser
        self.longConnectionHandler = longConnectionHandler
        self.chatGroupId2username = chatGroupId2username
        self.username2chatGroupId = username2chatGroupId
        self.RSACrypto = RSACrypto()
        self.mapping = {
            "GET/login" : self._handle_get_login,
            "POST/login": self._handle_post_login,
            "GET/chatroom": self._handle_get_chatroom,
            "GET/static": self._handle_get_static,
            "POST/connect": self._handle_establish_long_connection,
            "GET/favicon.ico": self._handle_get_favicon
        }

    def _handle_get_login(self,request,conn):
        responseTemplate = Response()
        if request.getSession() != None:
            responseTemplate.setSession("")
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
            conn=None,
        )
        self.loggedInUsers[username] = user
        response.setSession(username)
        response.sendRedirect(conn,location="/chatroom")

    def _handle_get_chatroom(self,request,conn):
        with open(TEMPLATE_PATH+"/chatroom.html","r") as fp:
            data = fp.read()
        data = data%PUBLIC_KEY
        response = Response()
        response.data = data
        response.sendHTML(conn)

    def _handle_get_favicon(self,request,conn):
        with open(STATIC_FILE_PATH + "/image/favicon.ico", "rb") as fp:
            file = fp.read()
        response = Response()
        response.data = file
        response.sendImage(conn,image_type="x-icon")

    def _handle_get_static(self,request,conn):
        params = request.params
        if "file_name" not in params:
            self._handle_default(request,conn)

        file_name = params.get("file_name")
        try:
            file_type = file_name.split(".")[1]
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
                with open(STATIC_FILE_PATH + "/image/" + file_name, "rb") as fp:
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

        # deny long connection if user is not logged-in
        if username is None or username not in self.loggedInUsers:
            self._handle_default(request,conn)
            return

        # deny long connection if the secret is not properly encrypted by the public key
        secret = None
        response = Response()
        try:
            encrypted_secret = request.data.get("secret")
            secret = self.RSACrypto.decrypt(encrypted_secret)
            assert (len(secret) == 16 or len(secret) == 24)
        except:
            response.data = {
                "status":0,
                "msg":"Secret exchange failed. Connection not established."
            }
            response.sendAjax(conn)
            return

        crypto = DESCrypto(secret)
        test_string = request.data.get("test_msg")
        if test_string is not None:
            decrypted_test_string = crypto.decrypt(test_string)
        else:
            decrypted_test_string = ""

        user = self.loggedInUsers[username]
        if user.first_time_request:
            user.first_time_request = False
            user.lastContactTime = time.time()
            user.crypto = crypto
            chatGroupId = str(uuid.uuid4())
            self.chatGroupId2username[chatGroupId] = [username]
            self.username2chatGroupId[username] = chatGroupId

            user.conn = conn
            thread = threading.Thread(target=self.longConnectionHandler.handle,args=(user,))
            thread.start()
            response.data = {
                "status":1,
                "msg":"connection established",
                "decrypted_test_msg": decrypted_test_string
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

    def dispatch(self,conn,request):
        path = request.path
        method = request.method
        handlingFunc = self.mapping.get(method+path)

        if handlingFunc is None:
            res = self._handle_default(request,conn)
        else:
            res = handlingFunc(request,conn)

        if res != "Don't close":
            conn.close()

    def handle(self,connection_queue):

        current_conn = None
        while True:
            if current_conn == None:
                if not connection_queue.empty():
                    current_conn = connection_queue.get()
                else:
                    time.sleep(SHORT_CONNECTION_SLEEP_CYCLE)
                    continue

            try:
                data = current_conn.recv(1024)
            except BlockingIOError as e:
                data = ""

            if len(data) > 0:
                request = Request.getRequest(data)
                print(f"[Short Connection] method: {request.method}; path: {request.path}")
                self.dispatch(current_conn,request)
                current_conn = None





