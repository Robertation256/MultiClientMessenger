from common.templates.Request import Request
from common.templates.Response import Response
from config import *
import time
import datetime
class LongConnectionHandler:

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
            "GET/send_message": self._handle_send_message,
            "GET/login": self._handle_get_login,
            "GET/connect": self._handle_get_connect,
            "GET/chatroom": self._handle_get_chatroom
        }


    def _logout(self,user):
        self.loggedInUsers.pop(user.name)
        groupId = self.username2chatGroupId[user.name]
        group_members = self.chatGroupId2username[groupId]
        self.username2chatGroupId.pop(user.name)
        if len(group_members) <= 1:
            self.chatGroupId2username.pop(groupId)
        else:
            self.chatGroupId2username.remove(user.name)

    def dispatch(self, request, user):
        path = request.path
        method = request.method
        handlingFunc = self.mapping.get(method + path)
        if handlingFunc is None:
            self._handle_default(request, user)
        else:
            handlingFunc(request, user)

    def _handle_get_chatroom(self,request,user):
        user.lastContactTime = time.time()
        with open(TEMPLATE_PATH+"\\chatroom.html","r") as fp:
            data = fp.read()
        response = Response()
        response.data = data
        response.sendHTML(user.conn)

    def _handle_get_connect(self,request,user):
        user.lastContactTime = time.time()
        response = Response()
        response.data = {
            "status":1,
            "msg": "Already connected"
        }
        response.headers["Connection"] = "Keep-Alive"
        response.sendAjax(user.conn)

    def _handle_get_login(self,request,user):
        responseTemplate = Response()
        if request.getSession() != None:
            responseTemplate.setSession("")
        with open(TEMPLATE_PATH + "/loginPage.html", "r", encoding="UTF-8") as fp:
            data = fp.read()
        responseTemplate.data = data
        responseTemplate.sendHTML(user.conn)
        self._logout(user)
        user.conn.close()
        return "logout"

    def _handle_refresh(self,request,user):
        print(f"handling refresh for user: {user.name}")
        user.lastContactTime = time.time()
        username = request.getSession()
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
            "my_chat_group_id": self.username2chatGroupId[username],
            "in_group_users":inGroupUserInfo,
            "out_group_users":outGroupUserInfo,
            "chat_messages": chatMessages
        }

        response = Response()
        response.data = result
        response.headers["Connection"] = "Keep-Alive"
        response.sendAjax(user.conn)


    def _handle_join(self,request,user):
        user.lastContactTime = time.time()
        username = request.getSession()
        targetGroupId = request.params.get("group_id")
        response = Response()
        response.headers["Connection"] = "Keep-Alive"
        if targetGroupId is None or targetGroupId not in self.chatGroupId2username:
            response.data = {
                "status":0,
                "msg":"Group id does not exist."
            }
            response.sendAjax(user.conn)
            return

        originalGroupId = self.username2chatGroupId[username]
        if originalGroupId == targetGroupId:
            response.data = {
                "status": 0,
                "msg": "You are already in this group chat."
            }
            response.sendAjax(user.conn)
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
        response.sendAjax(user.conn)


    def _handle_send_message(self,request,user):
        user.lastContactTime = time.time()
        username = request.getSession()
        groupId = self.username2chatGroupId.get(username)
        message = request.data.get("message")

        # todo: this part right now is nasty, add more error handling later
        if message != None and groupId is not None and len(self.chatGroupId2username.get(groupId)) > 1:
            message = {
                "timestamp":datetime.datetime.now().strftime("%m-%d %H:%M"),
                "username": username,
                "avatar_id": user.avatar_id,
                "message": message
            }
            if groupId in self.history_message:
                self.history_message[groupId].append(message)
            else:
                self.history_message[groupId] = [message]

    def _log(self):
        print("------------log------------")
        print(self.username2chatGroupId)
        print(self.chatGroupId2username)
        print(self.history_message)
        print("\n\n\n\n")

    def handle(self,user):
        while True:
            try:
                data = user.conn.recv(1024)
            except BlockingIOError as e:
                data = ""

            except OSError:
                print("[Long Connection] Connection with user {%s} is down."%user.name)
                break

            if len(data) > 0:
                request = Request.getRequest(data)
                print(f"[Long connection] user: {user.name}; method: {request.method}; path: {request.path}")
                res = self.dispatch(request,user)
                if res == "logout":
                    break
            else:
                time.sleep(LONG_CONNECTION_SLEEP_CYCLE)




