from common.handlers.PublicConnectionHandler import PublicConnectionHandler
from common.handlers.LoggedInUserHandler import LoggedInUserHandler
from common.templates.Response import Response
from config import *
import socket
import threading
from multiprocessing import Queue
import time
from common.templates.Request import Request
from concurrent.futures import ThreadPoolExecutor


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
        self.connectionQueue = Queue(maxsize=MAX_CONNECTION_QUEUE_SIZE)
        self.thread_pool = ThreadPoolExecutor(max_workers=MAX_THREAD_POOL_SIZE)

        # connection handler
        self.logged_in_user_handler = LoggedInUserHandler(
            self.loggedInUsers,
            self.chatGroupId2username,
            self.username2chatGroupId,
        )
        self.public_connection_handler = PublicConnectionHandler(
            self.loggedInUsers,
            self.logged_in_user_handler,
            self.chatGroupId2username,
            self.username2chatGroupId,
        )

    def connection_producer(self):
        while True:
            try:
                conn, addr = self.socket.accept()
                conn.setblocking(False)
                if not self.connectionQueue.full():
                    self.connectionQueue.put(conn)
                else:
                    self.turnDownConnection(conn)
            except OSError:
                time.sleep(CONNECTION_ACCEPT_SLEEP_TIME)

    def connection_consumer(self):
        blocked_start_time = time.time()
        current_conn = None
        while True:

            if current_conn == None:
                if not self.connectionQueue.empty():
                    current_conn = self.connectionQueue.get()
                else:
                    time.sleep(WAIT_FOR_CONNECTION_SLEEP_TIME)
            else:

                try:
                    data = current_conn.recv(2048)
                    request = Request.getRequest(data)
                    if request is not None:
                        self.thread_pool.submit(self.public_connection_handler.handle,current_conn,request)
                        # thread = threading.Thread(target=self.dispatch, args=(current_conn, request,))
                        # thread.start()
                        print(f"method: {request.method}; path: {request.path}")
                        current_conn = None
                        blocked_start_time = time.time()
                except BlockingIOError as e:
                    if time.time() - blocked_start_time > MAX_IO_BLOCK_TIME:
                        current_conn = None
                        blocked_start_time = time.time()


    def turnDownConnection(self,conn,msg="Service denied."):
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

    def kill_dead_client(self):
        while True:
            killSet = []
            for username, user in self.loggedInUsers.items():
                if not user.isAlive():
                    killSet.append(username)
            for username in killSet:
                if username in self.loggedInUsers:
                    self.logged_in_user_handler._logout(username)
                    print(f"[user: {username}] connection timeout")

            time.sleep(DEAD_CLIENT_KILL_PERIOD)


    def run(self):
        try:
            self.socket.bind((IP_ADDRESS, PORT_NUMBER))
            self.socket.listen(20)
        except:
            print("[server failed to start]")
            return

        # start connection consumer
        connectionConsumer = threading.Thread(target=self.connection_consumer)
        connectionConsumer.start()

        # start connection producer
        connectionProducer = threading.Thread(target=self.connection_producer)
        connectionProducer.start()

        #start the overwatch on dead connections
        deadClientKiller = threading.Thread(target=self.kill_dead_client)
        deadClientKiller.start()

        print(f"------------Server started on port {PORT_NUMBER}-----------------")







