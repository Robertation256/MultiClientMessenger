from common.templates.Response import Response
import time
from config import *
from queue import Queue
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
    ):
        self.loggedInUsers = loggedInUsers
        self.chatGroupId2username = chatGroupId2username
        self.username2chatGroupId = username2chatGroupId
        self.mapping = {
            "GET/refresh": self._handle_refresh,
            "GET/join": self._handle_join,
            "GET/unjoin": self._handle_unjoin,
            "POST/send_message": self._handle_send_message,
            "POST/connect": self._handle_establish_long_connection,
            "POST/log_out": self._handle_log_out
        }
        self.RSACrypto = RSACrypto()

    def _handle_unjoin(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers.get(username)
        response = Response()
        if user is None:
            response.data = {
                "status": 0,
                "msg": "Please log in first"
            }
            response.sendAjax(conn)
            return

        user.lastContactTime = time.time()
        original_group_id = self.username2chatGroupId.get(username)
        if original_group_id in self.chatGroupId2username:
            if len(self.chatGroupId2username[original_group_id])>1:
                self.chatGroupId2username[original_group_id].pop(username)
                user.message_queue = Queue()
                new_group_id = str(uuid.uuid4())
                self.chatGroupId2username[new_group_id] = [user.name]
                self.username2chatGroupId[user.name] = new_group_id
                response.data = {
                    "status": 1,
                    "msg": "Join succeeds."
                }
                response.sendAjax(conn)
                return

        response.data = {
            "status": 0,
            "msg": "Unjoin failed."
        }
        response.sendAjax(conn)



    def _handle_establish_long_connection(self,request,conn):
        username = request.getSession()

        # deny long connection if user is not logged-in
        if username is None or username not in self.loggedInUsers:
            self._handle_resource_not_found(request,conn)
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
            self._handle_resource_not_found(request,conn)

    def _handle_log_out(self,request,conn):
        username = request.getSession()
        response = Response()
        logged_out = self._logout(username)
        if logged_out:
            response.data = {
                "status": 1,
                "msg": "Log out succeeds"
            }
        else:
            response.data = {
                "status": 0,
                "msg": "User does not exist"
            }
        response.sendAjax(conn)

    def _logout(self,username):
        user = self.loggedInUsers.get(username)
        if user is None:
            return False

        try:
            self.loggedInUsers.pop(user.name)
            groupId = self.username2chatGroupId[user.name]
            group_members = self.chatGroupId2username[groupId]
            self.username2chatGroupId.pop(user.name)
        except:
            return False


        if len(group_members) <= 1:
            self.chatGroupId2username.pop(groupId)
        else:
            try:
                del self.chatGroupId2username[user.name]
            except:
                pass

        return True


    def _handle_refresh(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers.get(username)
        if user is None:
            return
        user.lastContactTime = time.time()
        username = request.getSession()
        if username not in self.username2chatGroupId:
            self._handle_resource_not_found(request,user)
            return

        chatGroupId = self.username2chatGroupId[username]
        inGroupUserNames = self.chatGroupId2username[chatGroupId]
        inGroupUserInfo = []
        outGroupUserInfo = []
        for name in inGroupUserNames:
            if name != username:
                try:
                    user = self.loggedInUsers[name]
                    entry = dict()
                    entry["username"] = user.name
                    entry["avatar_id"] = user.avatar_id
                    inGroupUserInfo.append(entry)
                except:
                    pass

        for name, other_user in self.loggedInUsers.items():
            # user outside current chat group
            if name not in inGroupUserNames and self.username2chatGroupId.get(name) is not None:
                entry = dict()
                entry["username"] = other_user.name
                entry["avatar_id"] = other_user.avatar_id
                entry["chat_group_id"] = self.username2chatGroupId[name]
                outGroupUserInfo.append(entry)

        chatMessages = []
        target_message_queue = self.loggedInUsers[username].message_queue
        message_num = REFRESH_MESSAGE_NUM
        while not target_message_queue.empty() and message_num >0:
            chatMessages.append(target_message_queue.get())
            message_num -= 1


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
        response.sendAjax(conn)

    def _handle_join(self,request,conn):
        username = request.getSession()
        user= self.loggedInUsers[username]
        user.lastContactTime = time.time()
        username = request.getSession()
        print(f"Join request from user {username}")
        targetGroupId = request.params.get("group_id")
        response = Response()
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
            del self.chatGroupId2username[originalGroupId]

        self.chatGroupId2username[targetGroupId].append(username)
        self.username2chatGroupId[username] = targetGroupId
        user.message_queue = Queue()

        response.data = {
            "status": 1,
            "msg": "Join succeeds."
        }
        response.sendAjax(conn)


    def _handle_send_message(self,request,conn):
        username = request.getSession()
        user = self.loggedInUsers[username]
        response = Response()
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


        print(f"[received message] {message}")


        # todo: this part right now is nasty, add more error handling later
        if groupId is not None and len(self.chatGroupId2username.get(groupId)) > 0:
            message = {
                "timestamp":datetime.datetime.now().strftime("%m-%d %H:%M:%S"),
                "username": username,
                "avatar_id": user.avatar_id,
                "message": message
            }
            if groupId in self.chatGroupId2username:
                usernames = self.chatGroupId2username[groupId]
                for username1 in usernames:
                    try:
                        user_ins = self.loggedInUsers[username1]
                        user_ins.message_queue.put(message)
                    except:
                        pass

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

    def _handle_resource_not_found(self,request,conn):
        rt = Response()
        rt.data = "404 not found"
        rt.send404(conn)

    def handle(self, conn, request):
        path = request.path
        method = request.method
        handler = self.mapping.get(method + path)

        if handler is None:
            self._handle_resource_not_found(request, conn)
        else:
            handler(request, conn)

        conn.close()






