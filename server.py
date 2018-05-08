#coding:utf-8
'''
file:server.py
date:2017/9/11 14:43
author:lockey
email:lockey@123.com
platform:win7.x86_64 pycharm python3
desc:p2p communication serverside
'''
import socketserver,json,time


connLst = []
groupLst = []
friendList = {}
##  代号 地址和端口 连接对象
#optype = {'ag':'group adding','cp':'chat with individual','cg':'chat with group'}
class Connector(object):   ##连接对象类
    def __init__(self,account, password, addrPort, conObj,stat):
        self.account = account
        self.password = password
        self.addrPort = addrPort
        self.conObj = conObj
        self.login_stat = stat

class Group(object):#群组类
    def __init__(self, groupname, groupOwner):
        self.groupId = 'group'+str(len(groupLst)+1)
        self.groupName = 'group'+groupname
        self.groupOwner = groupOwner
        self.createTime = time.time()
        self.members=[groupOwner]

class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        print("got connection from", self.client_address)
        userIn = False
        global connLst
        global groupLst
        while not userIn:
            conn = self.request
            data = conn.recv(1024)
            if not data:
                continue
            dataobj = json.loads(data.decode('utf-8'))
            print(dataobj)
            #如果连接客户端发送过来的信息格式是一个列表且注册标识为False时进行用户注册或者登陆
            ret = '0'
            #
            if type(dataobj) == list and not userIn:
                account = dataobj[0]
                password = dataobj[1]
                optype = dataobj[2]
                existuser = False
                passt = False
                if len(connLst) > 0:
                    for obj in connLst:
                        if obj.account == account:
                            existuser = True
                            if obj.password == password:
                                passt = True
                            break

                #if optype == 'login' and (not userIn or not existuser):
                if optype == 'login':
                    friends = []
                    #usr not exist
                    if (not existuser) :
                        ret = '1'
                    #usr has login
                    elif userIn:
                        ret = '2'
                        print('{}has been on {}'.format(account, self.client_address))
                    # password wrong
                    elif passt == False:
                        ret = '3'
                        print('password is wrong')
                    #login successfully
                    else:
                        ret = '0'
                        userIn = True
                        for obj in connLst:
                            if obj.account == account:
                                obj.addrPort = self.client_address
                                obj.conObj = conn
                                obj.login_stat = True
                                #给登录的用户发送好友列表
                                global friendList
                                print('list',friendList)
                                friends = friendList[obj.account]
                                print('nei',friends)

                    print('aaa{}.{}'.format(self.client_address, ret))
                    conn.sendall(ret.encode('utf-8'))

                    if ret == '0':
                        print('wai',friends)
                        send_data = {'type': 'getfriends', 'list': friends}
                        send_data = json.dumps(send_data)
                        print(send_data)
                        conn.sendall(send_data.encode('utf-8'))

                else:
                    if existuser:
                        ret = '1'
                        print('{} failed to register({}),account existed!'.format(account, self.client_address))
                    else:
                        try:
                            conObj = Connector(account,password,self.client_address,self.request, True)
                            connLst.append(conObj)
                            print('{} has registered to system({})'.format(account,self.client_address))
                            friendList.update({account: []})
                            userIn = True
                        except:
                            print('%s failed to register for exception!'%account)
                            ret = '99'
                    print('{}.{}'.format(self.client_address, ret))
                    conn.sendall(ret.encode('utf-8'))
                    if ret == '0':
                        break

        while True:
        #除登陆注册之外的请求的监听
            conn = self.request
            data = conn.recv(1024)
            if not data:
                continue
            print(data)
            dataobj = data.decode('utf-8')
            dataobj = json.loads(dataobj)

            if dataobj['type'] == 'q':
                print(self.client_address)
                for obj in connLst:
                    if obj.addrPort == self.client_address:
                        obj.login_stat = False
                        break
                conn.close()
                break

            # if dataobj['type'] == 'ag' and userIn:
            # #如果判断用户操作请求类型为添加群组则进行以下操作
            #     groupName = dataobj['groupName']
            #     groupObj = Group(groupName,self.request)
            #     groupLst.append(groupObj)
            #     conn.sendall('ag0'.encode('utf-8'))
            #     print('%s added'%groupName)
            #     continue
            #
            # if dataobj['type'] == 'eg' and userIn:
            # #入群操作
            #     groupName = dataobj['groupName']
            #     ret = 'eg1'
            #     for group in groupLst:
            #         if groupName == group.groupName:
            #             group.members.append(self.request)
            #             print('{} added into {}'.format(self.client_address,groupName))
            #             ret = 'eg0'
            #             break
            #     conn.sendall(ret.encode('utf-8'))
            #     continue

            #客户端将数据发给服务器端然后由服务器转发给目标客户端
            # print('connLst',connLst)
            # print('grouplst',groupLst)
            if len(connLst) > 1:
                sendok = False
                friend_in = True
                # if dataobj['type'] == 'cg':
                # #群内广播（除发消息的人）
                #     print('group',data)
                #     for obj in groupLst:
                #         if obj.groupName == dataobj['to']:
                #             for user in obj.members:
                #                 if user != self.request:
                #                     user.sendall(data)

                if dataobj['type'] == 'cp':
                #个人信息发送
                    friend_in = False
                    for obj in connLst:
                        if dataobj['to'] == obj.account and obj.login_stat:
                            obj.conObj.sendall(data)
                            friend_in = True
                            break
                    if friend_in ==False:
                        no_data ={'type': 'not_in', 'from': dataobj['to'], 'msg': dataobj['msg']}
                        no_data = json.dumps(no_data)
                        conn.sendall(no_data.encode('utf-8'))

                elif dataobj['type'] == 'picture':
                #个人信息发送
                    for obj in connLst:
                        if dataobj['to'] == obj.account and obj.login_stat:
                            obj.conObj.sendall(data)
                            has_sent=0
                            while has_sent < dataobj['msg']:
                                picData = conn.recv(1024)
                                has_sent+=len(picData)
                                obj.conObj.sendall(picData)
                                # print("has_sent ", has_sent)
                            break

                elif dataobj['type'] == 'afq':
                    friend_exist = False
                    friend_in = False
                    for obj in connLst:
                        if dataobj['to'] == obj.account :
                            if obj.login_stat :
                                obj.conObj.sendall(data)
                                friend_exist = True
                                friend_in = True
                            else:
                                friend_exist = True
                                friend_in = False

                    if friend_exist == False:
                        no_data = {'type': 'afr', 'from': dataobj['to'], 'to': dataobj['to'], 'response': 'notexist'}
                        no_data = json.dumps(no_data).encode('utf-8')
                        print(no_data)
                        conn.sendall(no_data)

                        print('not find friend')
                    elif friend_in == False:
                        no_data = {'type': 'afr', 'from': dataobj['to'], 'to': dataobj['to'], 'response': 'noin'}
                        no_data = json.dumps(no_data).encode('utf-8')
                        print(no_data)
                        conn.sendall(no_data)

                elif dataobj['type'] == 'afr':
                    #添加好友
                    if dataobj['response'] == '1':
                        friendList[dataobj['to']].append(dataobj['from'])
                        friendList[dataobj['from']].append(dataobj['to'])
                        print('new add',friendList)
                    for obj in connLst:
                        if dataobj['to'] == obj.account:
                            obj.conObj.sendall(data)
                else:
                    pass
            else:
                conn.sendall('-1'.encode('utf-8'))
                continue

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1',8022),MyServer)
    print('waiting for connection...')
    server.serve_forever()# -*- coding: utf-8 -*-
