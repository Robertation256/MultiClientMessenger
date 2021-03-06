'''
A prototype for logged-in users
'''
from config import *
import time
from queue import Queue

class User:
    def __init__(self,conn,name,avatar_id):
        self.conn = conn
        self.name = name
        self.avatar_id = avatar_id
        self.first_time_request = True
        self.lastContactTime = time.time()
        self.crypto = None
        self.message_queue = Queue()
    def isAlive(self):
        '''
        Checks if a client is still active
        By default, a client should send refresh request every 2 sec
        :return:
        '''
        return time.time()-self.lastContactTime <= USER_TIMEOUT
