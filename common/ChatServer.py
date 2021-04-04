from common.handlers.ShortConnectionHandler import ShortConnectionHandler
from common.handlers.LongConnectionHandler import LongConnectionHandler
from common.templates.Request import Request
from common.templates.Response import Response
from dto.User import User
import socket
import threading
from multiprocessing import Queue
import time
import ctypes


class ChatServer():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.loggedInUsers = dict()
        self.loggedInUserThreads = dict()
        self.shortConnectionHandler = ShortConnectionHandler(self.loggedInUsers)
        self.connectionQueue = Queue(maxsize=100)

    def turnDownConnection(self,conn,msg=""):
        response = Response()
        response.data = {
            "status":0,
            "msg":msg
        }
        response.sendAjax(conn)
        conn.close()

    def login(self,conn,request):
        data = request.data
        username = data["username"]
        if username in self.loggedInUsers:
            self.turnDownConnection(conn,msg="username already exists")
            return

        avatar_id = data["avatar_id"]
        user = User(
            name=username,
            avatar_id=avatar_id,
            conn=conn,
            lastContactTime=time.time()
        )
        self.loggedInUsers[username] = user
        longConnectionHandler = LongConnectionHandler()
        thread = threading.Thread(target=longConnectionHandler.handle,args=(user,))
        self.loggedInUserThreads[username] = thread
        thread.start()



    def handleShortConnection(self):
        while True:
            if not self.connectionQueue.empty():

                conn = self.connectionQueue.get(block=True)
                data = conn.recv(1024)
                request = Request.getRequest(data)
                print(f"[Short connection handler] {request.method} {request.path}")

                res = self.shortConnectionHandler.handle(conn,request)

                if res:
                    self.login(conn,request)
                    res.sendRedirect(conn, location="/chatroom")



    def killThread(self,thread):
        tid = thread.ident
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def killDeadClient(self):
        while True:
            killSet = []
            for username, user in self.loggedInUsers.items():
                if not user.isAlive():
                    killSet.append(username)

            for username in killSet:
                thread = self.loggedInUserThreads.pop(username)
                conn = self.loggedInUsers.pop(username).conn
                self.killThread(thread)
                conn.close()
                print(f"Killed dead user: {username}")
            time.sleep(10)




    def run(self):
        try:
            self.socket.bind(("localhost",80))
            self.socket.listen(20)
        except:
            print("[server failed to start]")
            return

        #start the connection consumer thread
        connectionConsumer = threading.Thread(target=self.handleShortConnection)
        connectionConsumer.start()


        #start the overwatch on dead connections
        deadClientKiller = threading.Thread(target=self.killDeadClient)
        deadClientKiller.start()


        while True:
            conn, clientAddress = self.socket.accept()
            if not self.connectionQueue.full():
                self.connectionQueue.put(conn,block=True)
            else:
                self.turnDownConnection(conn)
                time.sleep(1)





