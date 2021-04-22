from common.templates.Response import Response
import time
import uuid
import datetime
import json
from utils.RSACrypto import RSACrypto
from utils.DESCrypto import DESCrypto



class LoggedInUserHandler:

    def __init__(self,
                 loggedInUsers,
                 chatGroupId2username,
                 username2chatGroupId,
                 history_message
    ):
        self.loggedInUsers = loggedInUsers
        self.chatGroupId2username = chatGroupId2username
        self.username2chatGroupId = username2chatGroupId
        self.history_message = history_message
        self.mapping = {
            "GET/refresh": self._handle_refresh,
            "GET/join": self._handle_join,
            "POST/send_message": self._handle_send_message,
            "POST/connect": self._handle_establish_long_connection,

        }
        self.RSACrypto = RSACrypto()


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

            response.data = {
                "status":1,
                "msg":"connection established",
                "decrypted_test_msg": decrypted_test_string
            }
            response.sendAjax(conn)
        else:
            self._handle_default(request,conn)


    def _logout(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers[username]

        self.loggedInUsers.pop(user.name)
        groupId = self.username2chatGroupId[user.name]
        group_members = self.chatGroupId2username[groupId]
        self.username2chatGroupId.pop(user.name)
        if len(group_members) <= 1:
            self.chatGroupId2username.pop(groupId)
        else:
            self.chatGroupId2username.remove(user.name)

    def dispatch(self, request, conn):
        path = request.path
        method = request.method
        handlingFunc = self.mapping.get(method + path)
        if handlingFunc is None:
            self._handle_default(request, conn)
        else:
            handlingFunc(request, conn)

    def _handle_default(self,request,conn):
        rt = Response()
        rt.headers["Connection"] = "Keep-Alive"
        rt.data = "404 not found"
        rt.send404(conn)

    def _handle_refresh(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers[username]
        user.lastContactTime = time.time()
        username = request.getSession()
        print(f"refresh request from     user: {username} ")
        if username not in self.username2chatGroupId:
            self._handle_default(request,user)
            return

        chatGroupId = self.username2chatGroupId[username]
        inGroupUserNames = self.chatGroupId2username[chatGroupId]
        inGroupUserInfo = []
        outGroupUserInfo = []
        for name in inGroupUserNames:
            if name != username:
                user = self.loggedInUsers[name]
                entry = dict()
                entry["username"] = user.name
                entry["avatar_id"] = user.avatar_id
                inGroupUserInfo.append(entry)

        for name, other_user in self.loggedInUsers.items():
            # user outside current chat group
            if name not in inGroupUserNames and self.username2chatGroupId.get(name) is not None:
                entry = dict()
                entry["username"] = other_user.name
                entry["avatar_id"] = other_user.avatar_id
                entry["chat_group_id"] = self.username2chatGroupId[name]
                outGroupUserInfo.append(entry)

        chatMessages = self.history_message.get(chatGroupId,[])

        result = {
            "username": username,
            "in_group_users":inGroupUserInfo,
            "out_group_users":outGroupUserInfo,
            "chat_messages": chatMessages
        }

        json_string = json.dumps(result)
        encrypted_result = user.crypto.encrypt(json_string)
        response = Response()
        response.data = encrypted_result
        response.headers["Connection"] = "Keep-Alive"
        response.sendAjax(conn)

    def _handle_join(self,request,conn):
        username = request.getSession()
        user= self.loggedInUsers[username]
        user.lastContactTime = time.time()
        username = request.getSession()
        print(f"Join request from user {username}")
        targetGroupId = request.params.get("group_id")
        response = Response()
        response.headers["Connection"] = "Keep-Alive"
        if targetGroupId is None or targetGroupId not in self.chatGroupId2username:
            response.data = {
                "status":0,
                "msg":"Group id does not exist."
            }
            response.sendAjax(conn)
            return

        originalGroupId = self.username2chatGroupId[username]
        if originalGroupId == targetGroupId:
            response.data = {
                "status": 0,
                "msg": "You are already in this group chat."
            }
            response.sendAjax(conn)
            return

        self.chatGroupId2username[originalGroupId].remove(username)
        if len(self.chatGroupId2username[originalGroupId]) < 1:
            self.chatGroupId2username.pop(originalGroupId)
            if originalGroupId in self.history_message:
                self.history_message.pop(originalGroupId)
        self.chatGroupId2username[targetGroupId].append(username)
        self.username2chatGroupId[username] = targetGroupId

        response.data = {
            "status": 1,
            "msg": "Join succeeds."
        }
        response.sendAjax(conn)


    def _handle_send_message(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers[username]
        response = Response()
        response.headers["Connection"] = "Keep-Alive"
        user.lastContactTime = time.time()
        username = request.getSession()
        groupId = self.username2chatGroupId.get(username)
        try:
            message = request.data["message"]
            message = user.crypto.decrypt(message)
        except:
            response.data = {
                "status":0,
                "msg": "message send failed. Bad message."
            }
            response.sendAjax(conn)
            return


        # todo: this part right now is nasty, add more error handling later
        if groupId is not None and len(self.chatGroupId2username.get(groupId)) > 0:
            message = {
                "timestamp":datetime.datetime.now().strftime("%m-%d %H:%M:%S"),
                "username": username,
                "avatar_id": user.avatar_id,
                "message": message
            }
            if groupId in self.history_message:
                self.history_message[groupId].append(message)
            else:
                self.history_message[groupId] = [message]

            response.data = {
                "status": 1,
                "msg": "message send succeeds"
            }
            response.sendAjax(conn)
            return

        response.data = {
            "status": 0,
            "msg": "message send failed. Bad group id"
        }
        response.sendAjax(conn)


    def handle(self,request,conn):
        self.dispatch(request,conn)
        conn.close()


        # while True:
        #     try:
        #         data = user.conn.recv(1024)
        #     except BlockingIOError as e:
        #         data = ""
        #
        #     except OSError:
        #         print("[Long Connection] Connection with user {%s} is down."%user.name)
        #         break
        #
        #     if len(data) > 0:
        #         request = Request.getRequest(data)
        #         #print(f"[Long connection] user: {user.name}; method: {request.method}; path: {request.path}")
        #         res = self.dispatch(request,user)
        #         if res == "logout":
        #             break
        #     else:
        #         time.sleep(LONG_CONNECTION_SLEEP_CYCLE)




