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
        # memory storage
        self.loggedInUsers = dict()
        self.chatGroupId2username = dict()
        self.username2chatGroupId = dict()
        self.history_message = dict()

        # infrastructure
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectionQueue = Queue(maxsize=100)
        self.loggedInUserThreads = dict()
        self.longConnectionHandler = LongConnectionHandler(
            self.chatGroupId2username,
            self.username2chatGroupId,
            self.history_message
        )
        self.shortConnectionHandler = ShortConnectionHandler(
            self.loggedInUsers,
            self.loggedInUserThreads,
            self.longConnectionHandler
        )






    def turnDownConnection(self,conn,msg=""):
        response = Response()
        response.data = {
            "status":0,
            "msg":msg
        }
        response.sendAjax(conn)
        conn.close()

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
                if username in self.loggedInUserThreads:
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





