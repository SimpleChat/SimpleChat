import tkinter as tk
from tkinter import ttk
import time
import os
import threading, json
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

class MainPage(object):
    def __init__(self, master=None, tcpCliSock=None,username=None ):
        self.root = master #定义内部变量root
        self.root.geometry('%dx%d' % (550, 400)) #设置窗口大小
        self.root.grid_propagate(0)

        self.friendList = []
        self.createMainPage()
        self.photo = None
        self.userAccount = username.get()
        self.tcpCliSock =tcpCliSock
        self.root.protocol('WM_DELETE_WINDOW', self.closeMainWindow)
        self.thread1 = threading.Thread(target=self.run)
        self.thread1.start()
        self.filename = None
        self.picNum = 0
        self.loadSucc = False
        self.picList = []


    def closeMainWindow(self):
        ans = tk.messagebox.askyesno(title="提示", message="确定要退出程序？")
        if ans:
            dataObj = {'type': 'q', 'from':self.userAccount}
            dataObj = json.dumps(dataObj)
            self.tcpCliSock.send(dataObj.encode('utf-8'))
            self.tcpCliSock.shutdown(2)
            self.tcpCliSock.close()
            self.root.destroy()
        else:
            pass

    def message(self):                  #弹出窗口
        friendname = self.entrySerch.get()
        if len(friendname) == 0:
            tk.messagebox.showinfo("提示", "请输入要添加好友的名称")
        elif friendname == self.userAccount:
            tk.messagebox.showinfo("提示", "不能添加自己为好友")
        else:
            if friendname not in self.friendList:
                dataObj = {'type': 'afq', 'from': self.userAccount, 'to': friendname}
                dataObj = json.dumps(dataObj)
                self.tcpCliSock.send(dataObj.encode('utf-8'))
            else:
                tk.messagebox.showinfo("提示",friendname + "已经是您的好友")

    def chat(self, target):
#进入聊天（群聊和点对点聊天可以选择）
        print('{}->{}: '.format(self.userAccount,target))
        msg = self.txtMsg.get(0.0, tk.END)[:-1]
        self.txtMsg.delete(0.0, tk.END)
        # target = str(target.encode("utf-8"))

        if len(msg) > 0 :
            strMsg = self.userAccount + ' : ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime()) + '\n'
            self.txtMsgList.config(state=tk.NORMAL)
            self.txtMsgList.insert(tk.END, strMsg, 'greencolor')   #插入到tag位置
            self.txtMsgList.insert(tk.END, msg)
            self.txtMsgList.insert(tk.END, "\n")
            # self.txtMsg.delete(0.0, tk.END)
            self.txtMsgList.config(state=tk.DISABLED)

            optype = 'cp'
            dataObj = {'type': optype, 'to': target, 'msg': msg, 'froms': self.userAccount}
            datastr = json.dumps(dataObj)
            self.tcpCliSock.send(datastr.encode('utf-8'))
        else:
            tk.messagebox.showinfo(title='提示', message='输入内容不能为空!')

    def sendMsg(self):                  #发送消息
        if(self.friend == "双击选择好友发送消息"):
            tk.messagebox.showinfo(title='提示', message='双击选择好友发送消息!')
        else:
            self.chat(self.friend)

    def cancelMsg(self):                #取消消息
        self.txtMsg.delete('0.0', tk.END)

    def loadPic(self):
        self.filename = askopenfilename(filetypes=({
                ("图片格式",".jpg"),("图片格式",".png"),("图片格式",".gif")
                }))
        print(self.filename)
        photo = Image.open(self.filename)
        if photo.width < photo.height: # 纵向
            out = photo.resize((60, int(photo.height / photo.width * 60.0)), Image.ANTIALIAS)
        else:
            out = photo.resize((int(photo.width / photo.height * 60.0), 60), Image.ANTIALIAS) # 横向
        self.photo = ImageTk.PhotoImage(out)
        self.picList.append(self.photo)

        self.txtMsg.image_create(tk.END,image=self.picList[-1])
        self.loadSucc = True
        # 用这个方法创建一个图片对象，并插入到“END”的位置

    def sendPic(self):
        if(self.friend == "双击选择好友发送消息"):
            tk.messagebox.showinfo(title='提示', message='双击选择好友发送消息!')
        elif self.loadSucc:
            file_size = os.stat(self.filename).st_size
            print(file_size)
            optype = 'picture'
            dataObj = {'type': optype, 'to': self.friend, 'msg': file_size, 'froms': self.userAccount}

            datastr = json.dumps(dataObj)
            self.tcpCliSock.send(datastr.encode('utf-8'))

            sendPicture = open(self.filename,'rb')
            while 1:
                data = sendPicture.read(1024)
                if not data:
                    print('{0} file send over...'.format(self.filename))
                    break
                self.tcpCliSock.send(data)
            sendPicture.close()

            self.txtMsg.delete('0.0', tk.END)
            recvStrMsg = dataObj['froms'] + ' : ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime()) + '\n'
            self.txtMsgList.config(state=tk.NORMAL)
            self.txtMsgList.insert(tk.END, recvStrMsg, 'greencolor')   #插入到tag位置

            self.txtMsgList.image_create(tk.END,image=self.photo)
            # 用这个方法创建一个图片对象，并插入到“END”的位置
            self.txtMsgList.insert(tk.END, "\n")
            self.txtMsgList.config(state=tk.DISABLED)
        else:
            tk.messagebox.showinfo(title='提示', message='请选择图片!')

    def chatWithFriend(self, detail):
        # print(detail)
        indexs = self.listLianxi.curselection()
        if len(indexs) > 0 :
            selectFriend = str(self.listLianxi.get(indexs[0])[17:])


            if(selectFriend != self.friend):
                # print("\nself.friend ", self.friend)
                # print("\nselect f ", selectFriend)
                self.friend = selectFriend
                self.txtMsgList.config(state=tk.NORMAL)
                self.txtMsgList.delete(0.0, tk.END)
                self.txtMsgList.config(state=tk.DISABLED)

        else:
            self.friend = "双击选择好友发送消息"
        self.messageLabel["text"]=self.friend

    def flushFriend(self):
        self.listLianxi.delete(0, tk.END)
        self.friendList.sort()
        for line in self.friendList:
            self.listLianxi.insert(tk.END, "  联系人   ------   " + str(line))

    def run(self):
        #接收数据线程
        while True:
            # print(self.tcpCliSock)
            data = self.tcpCliSock.recv(1024).decode('utf-8')
            if not data:
                continue
            if data[-1] == '0':
                data = data[0:-1]
            dataObj = json.loads(data)

            if data == "-1":
                print('can not connect to target!')
                # recvStrMsg = self.userAccount + ' : ' + time.strftime("%Y-%m-%d %H:%M:%S",
                #                               time.localtime()) + '\n'
                self.txtMsgList.config(state=tk.NORMAL)
                # self.txtMsgList.insert(tk.END, recvStrMsg, 'bluecolor')   #插入到tag位置
                self.txtMsgList.insert(tk.END, "请添加好友！", 'redcolor')
                self.txtMsgList.insert(tk.END, "\n")
                self.txtMsgList.config(state=tk.DISABLED)
                continue


            print('?',dataObj)
            # 添加请求
            if dataObj['type'] == 'afq':
                req_from = dataObj['from']
                ans = tk.messagebox.askyesno(title="好友请求", message=req_from + "请求添加您为好友")
                if ans:
                    rep = '1'
                    if req_from not in self.friendList:
                        self.friendList.append(req_from)
                        self.flushFriend()
                else:
                    rep = '0'
                print('{} wants to add you as a friend'.format(req_from))

                data_send = {'type': 'afr', 'from': self.userAccount, 'to':req_from, 'response': rep}
                data_send = json.dumps(data_send).encode('utf-8')
                self.tcpCliSock.send(data_send)
            #加好友回复
            if dataObj['type'] == 'afr':
                rep_from = dataObj['from']
                resp = dataObj['response']
                if resp == 'notexist':
                    print("{} not exist".format(rep_from))
                    tk.messagebox.showinfo('提示', '用户不存在！')
                elif resp == '0':
                    tk.messagebox.showinfo('提示', '用户拒绝了您的请求！')
                    print("{} refused your request".format(rep_from))
                elif resp == '1':
                    tk.messagebox.showinfo('提示', rep_from + '已经成为您的好友！')
                    print('{} has become your friend'.format(rep_from))
                    self.friendList.append(rep_from)
                    self.flushFriend()
            # 获取好友列表
            if dataObj['type'] == 'getfriends':
                print(dataObj['list'])
                self.friendList = dataObj['list']
                self.flushFriend()

            if dataObj['type'] == 'not_in':
                print('{} is not online'.format(dataObj['from']))
                print('{} send failed'.format(dataObj['msg']))
                self.txtMsgList.config(state=tk.NORMAL)
                # self.txtMsgList.insert(tk.END, recvStrMsg, 'bluecolor')   #插入到tag位置
                self.txtMsgList.insert(tk.END, "消息发送失败！", 'redcolor')
                self.txtMsgList.insert(tk.END, "\n")
                self.txtMsgList.config(state=tk.DISABLED)

            if dataObj['type'] == 'cp':
            #个人消息的格式定义
                print('{} ->{} : {}'.format(dataObj['froms'], self.userAccount, dataObj['msg']))

                recvStrMsg = dataObj['froms'] + ' : ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime()) + '\n'
                self.txtMsgList.config(state=tk.NORMAL)
                self.txtMsgList.insert(tk.END, recvStrMsg, 'bluecolor')   #插入到tag位置
                self.txtMsgList.insert(tk.END, dataObj['msg'])
                self.txtMsgList.insert(tk.END, "\n")
                self.txtMsgList.config(state=tk.DISABLED)
            elif dataObj['type'] == 'picture':
                recvStrMsg = dataObj['froms'] + ' : ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime()) + '\n'
                self.txtMsgList.config(state=tk.NORMAL)
                self.txtMsgList.insert(tk.END, recvStrMsg, 'bluecolor')   #插入到tag位置

                print("recieve    :",dataObj)
                has_received=0
                filesize = dataObj['msg']
                recvPic = open('./tempPicture/tempPic_' +str(self.picNum), 'wb')
                while(has_received != filesize) :
                    if filesize - has_received > 1024:
                        recvData = self.tcpCliSock.recv(1024)
                        has_received += len(recvData)
                    else:
                        recvData = self.tcpCliSock.recv(filesize - has_received)
                        has_received = filesize
                    # print("has_received  ", has_received)
                    recvPic.write(recvData)
                recvPic.close()

                photo = Image.open("./tempPicture/tempPic_" + str(self.picNum))
                self.picNum += 1
                if photo.width < photo.height: # 纵向
                    out = photo.resize((60, int(photo.height / photo.width * 60.0)), Image.ANTIALIAS)
                else:
                    out = photo.resize((int(photo.width / photo.height * 60.0), 60), Image.ANTIALIAS) # 横向
                self.photo = ImageTk.PhotoImage(out)

                self.picList.append(self.photo)

                self.txtMsgList.image_create(tk.END,image=self.picList[-1])
                # 用这个方法创建一个图片对象，并插入到“END”的位置
                self.txtMsgList.insert(tk.END, "\n")
                self.txtMsgList.config(state=tk.DISABLED)


    def createMainPage(self):
        ###******创建frame容器******###
        #第一列
        self.frmA1 = tk.Frame(width=180, height=30)
        self.frmA2 = tk.Frame(width=180, height=300)
        self.frmA3 = tk.Frame(width=180, height=30)
        #第二列
        self.frmB1 = tk.Frame(width=320, height=30)
        self.frmB2 = tk.Frame(width=320, height=180)
        self.frmB3 = tk.Frame(width=320, height=120)
        self.frmB4 = tk.Frame(width=320, height=30)

        ###******创建控件******###
        #Text控件
        self.txtMsgList = tk.Text(self.frmB2, height=13, width=42)       #frmB2表示父窗口
        self.txtMsgList.tag_config('greencolor',               #标签tag名称
                        foreground='#008C00')       #标签tag前景色，背景色为默认白色
        self.txtMsgList.tag_config('bluecolor',               #标签tag名称
                        foreground='#6495ED')       #标签tag前景色，背景色为默认白色
        self.txtMsgList.tag_config('redcolor',               #标签tag名称
                        foreground='#FF0000')       #标签tag前景色，背景色为默认白色
        self.txtMsgList.config(state=tk.DISABLED)

        self.txtMsg = tk.Text(self.frmB3, height=9, width=42);

        #Button控件
        self.btnPic = ttk.Button(self.frmB4, text='选择图片', width = 8,
                                 command = self.loadPic
                                 )
        self.btnFile = ttk.Button(self.frmB4, text='发送图片', width = 8,
                                 command = self.sendPic
                                 )
        self.btnSend = ttk.Button(self.frmB4, text='发 送', width = 8,
                                 command = self.sendMsg
                                 )
        self.btnCancel = ttk.Button(self.frmB4, text='取消', width = 8,
                                   command = self.cancelMsg
                                   )
        self.btnSerch=ttk.Button(self.frmA3, text='添加好友',        #button的显示内容
                      width = 9,
                      command = self.message)                 #回调函数

        #Entry控件
        self.entrySerch= ttk.Entry(self.frmA3, width=14) #输入

        #Scrollbar控件
        self.scroLianxi = tk.Scrollbar(self.frmA2,width=22,troughcolor="blue")
        self.scroMessage = tk.Scrollbar(self.frmB2,width=22,troughcolor="blue")
        self.scroSendMessage = tk.Scrollbar(self.frmB3,width=22,troughcolor="blue")

        #Listbox控件
        self.listLianxi = tk.Listbox(self.frmA2, width=22,height=16,
                      yscrollcommand = self.scroLianxi.set )  #连接listbox 到 vertical scrollbar

        self.listLianxi.bind('<Button-1>',self.chatWithFriend)#绑定鼠标左键点击事件

        self.scroLianxi.config( command = self.listLianxi.yview )   #scrollbar滚动时listbox同时滚动
        self.scroMessage.config( command = self.txtMsgList.yview )   #scrollbar滚动时listbox同时滚动
        self.scroSendMessage.config( command = self.txtMsg.yview )   #scrollbar滚动时listbox同时滚动
        self.txtMsgList.config(yscrollcommand = self.scroMessage.set)
        self.txtMsg.config(yscrollcommand = self.scroSendMessage.set)

        #Label控件
        self.listLabel = tk.Label(self.frmA1, text='通讯录', width=20,height=1)
        self.friend = "双击选择好友发送消息"
        self.messageLabel = tk.Label(self.frmB1, text= self.friend, width=40,height=1)


        ###******窗口布局******###
        self.frmA1.grid(row=0, column=0, padx=10, pady=10)
        self.frmA2.grid(row=1, column=0, padx=10, rowspan=2)
        self.frmA3.grid(row=3, column=0, padx=10, pady=10)

        self.frmB1.grid(row=0, column=1, padx=10, pady=10)
        self.frmB2.grid(row=1, column=1, padx=10)
        self.frmB3.grid(row=2, column=1, padx=10)
        self.frmB4.grid(row=3, column=1, padx=10, pady=10)

        #固定大小
        self.frmA1.grid_propagate(0)
        self.frmA2.grid_propagate(0)
        self.frmA3.grid_propagate(0)
        self.frmB1.grid_propagate(0)
        self.frmB2.grid_propagate(0)
        self.frmB3.grid_propagate(0)
        self.frmB4.grid_propagate(0)

        ###******控件布局******###
        self.txtMsgList.grid(row=0,column=0)
        self.txtMsg.grid(row=0,column=0)

        self.btnPic.grid(row=0, column=0)
        self.btnFile.grid(row=0, column=1)
        self.btnSend.grid(row=0, column=2)
        self.btnCancel.grid(row=0, column=3)

        self.btnSerch.grid(row=0,column=1)
        self.entrySerch.grid(row=0,column=0)

        self.listLianxi.grid(row=0,column=0)
        self.scroLianxi.grid(row=0,column=1,ipady=125,sticky=tk.N)

        self.scroMessage.grid(row=0,column=1,ipady=65,pady=0,sticky=tk.N)
        self.scroSendMessage.grid(row=0,column=1,ipady=35,pady=0,sticky=tk.N)

        self.listLabel.grid(ipadx=6, ipady=6)
        self.messageLabel.grid(ipadx=10, ipady=6)
