from common.handlers.ShortConnectionHandler import ShortConnectionHandler
from common.handlers.LongConnectionHandler import LongConnectionHandler
from common.templates.Response import Response
from config import *
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
        self.socket.setblocking(False)
        self.connectionQueue = Queue(maxsize=100)
        # self.loggedInUserThreads = dict()
        self.longConnectionHandler = LongConnectionHandler(
            self.loggedInUsers,
            self.chatGroupId2username,
            self.username2chatGroupId,
            self.history_message
        )
        self.shortConnectionHandler = ShortConnectionHandler(
            self.loggedInUsers,
            self.longConnectionHandler,
            self.chatGroupId2username,
            self.username2chatGroupId,
        )






    def turnDownConnection(self,conn,msg=""):
        response = Response()
        response.data = {
            "status":0,
            "msg":msg
        }
        response.sendAjax(conn)
        conn.close()

    # def killThread(self,thread):
    #     tid = thread.ident
    #     """raises the exception, performs cleanup if needed"""
    #     tid = ctypes.c_long(tid)
    #     res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    #     if res == 0:
    #         raise ValueError("invalid thread id")
    #     elif res != 1:
    #         # """if it returns a number greater than one, you're in trouble,
    #         # and you should call it again with exc=NULL to revert the effect"""
    #         ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
    #         raise SystemError("PyThreadState_SetAsyncExc failed")

    def killDeadClient(self):
        while True:
            killSet = []
            for username, user in self.loggedInUsers.items():
                if not user.isAlive() and user.conn is not None:
                    killSet.append(username)

            for username in killSet:
                if username in self.loggedInUsers:
                    # notice: there is no need to kill the thread here
                    # the thread will return if connection is down

                    # thread = self.loggedInUserThreads.pop(username)
                    # self.killThread(thread)
                    conn = self.loggedInUsers.pop(username).conn
                    print(f"[Long Connection]: Connection timeout with user {username}\n----------closing connection-----------")
                    conn.close()

            time.sleep(DEAD_CLIENT_KILL_CYCLE)


    def run(self):
        try:
            self.socket.bind((IP_ADDRESS, PORT_NUMBER))
            self.socket.listen(20)
        except:
            print("[server failed to start]")
            return

        #start the connection consumer thread
        connectionConsumer = threading.Thread(target=self.shortConnectionHandler.handle, args=(self.connectionQueue,))
        connectionConsumer.start()

        #start the overwatch on dead connections
        deadClientKiller = threading.Thread(target=self.killDeadClient)
        deadClientKiller.start()

        print(f"------------Server started on port {PORT_NUMBER}-----------------")


        while True:

            try:
                conn, clientAddress = self.socket.accept()
                conn.setblocking(False)
                # conn.settimeout(1)
                if not self.connectionQueue.full():
                    self.connectionQueue.put(conn)
                else:
                    self.turnDownConnection(conn)
            except OSError:
                time.sleep(CONNECTION_ACCEPT_SLEEP_CYCLE)






