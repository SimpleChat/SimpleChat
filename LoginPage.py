from tkinter import *
from tkinter.messagebox import *

from socket import *
import threading,sys,json,re
from MainPage import *

##socket
HOST = '127.0.0.1'
PORT = 8022
BUFFERSIZE = 1024
ADDR = (HOST, PORT)
myre = r"^[_a-zA-Z]\w{0,}"
tcpClintSock = socket(AF_INET, SOCK_STREAM)

class LoginPage(object):
    def __init__(self, master=None, tcpCliSock = None):
        self.root = master #定义内部变量root
        self.root.geometry('%dx%d+%d+%d' % (300, 200, 500, 250)) #设置窗口大小
        self.username = StringVar()
        self.password = StringVar()
        self.createPage()
        self.root.protocol('WM_DELETE_WINDOW', self.closeWindow)
        self.tcpCliSock = tcpCliSock

    def createPage(self):
        self.page = Frame(self.root) #创建Frame
        self.page.pack()
        Label(self.page).grid(row=0, sticky=W)
        Label(self.page, text = '账户: ').grid(row=1, column=1,sticky=W, pady=10)
        Entry(self.page, textvariable=self.username).grid(row=1, column=2, sticky=E)
        Label(self.page, text = '密码: ').grid(row=2, column=1,sticky=W, pady=10)
        Entry(self.page, textvariable=self.password, show='*').grid(row=2, column=2, sticky=E)
        ttk.Button(self.page, text='注册', command=self.register).grid(row=3,column=1, sticky=W, pady=10)
        ttk.Button(self.page, text='登陆', command=self.login).grid(row=3, column=2, sticky=E)
    def register(self):
        if not self.re_check():
            return None
        else:
            name = self.username.get()
            secret = self.password.get()
            if len(name)==0 or len(secret)==0:
                showinfo(title='错误', message='账号和密码不能为空！')
            else:
                regInfo = [name, secret, 'register']
                datastr = json.dumps(regInfo)
                self.tcpCliSock.send(datastr.encode('utf-8'))
                data =self.tcpCliSock.recv(BUFFERSIZE)
                data = data.decode()
                print("rrrrrrrr  :", data)

                if data == '0':
                    print('success to register!')
                    showinfo(title='成功', message='恭喜您注册成功！')
                    # self.page.quit()
                    self.page.destroy()
                    MainPage(self.root, self.tcpCliSock, self.username)
                    # return True
                elif data == '1':
                    print('Failed to register, account existed!')
                    showinfo(title='错误', message='账号已存在，注册失败')
                    return False
                else:
                    print('Failed for exceptions!')
                    showinfo(title='错误', message='服务器出错！')
                    return False

    def login(self):
        name = self.username.get()
        secret = self.password.get()

        if len(name) == 0 or len(secret) == 0:
            showinfo(title='错误', message='账号和密码不能为空！')
        else:
            loginInof = [name, secret, 'login']
            datastr = json.dumps(loginInof)
            self.tcpCliSock.send(datastr.encode('utf-8'))
            data = self.tcpCliSock.recv(BUFFERSIZE).decode()
            print("llllll  :", data)
            # 0:ok, 1:usr not exist, 2:usr has logged in

            if data == '0':
                print('Success to login!{}'.format(data))
                showinfo(title='成功',message='登录成功！')
                self.page.destroy()
                MainPage(self.root, self.tcpCliSock, self.username)
            elif data == '1':
                print('Failed to login in(user not exist or username not match the password)!')
                showinfo(title='错误', message='登录失败，请检查用户名和密码')
                return False
            elif data == '2':
                print('you have been online!')
                showinfo(title='错误', message='您已登录，不可重复登录')
                return False
            elif data == '3':
                print('secret wrong!')
                showinfo(title='错误', message='密码错误')
                return False

    def re_check(self):
        name = self.username.get()
        secret = self.username.get()
        if not re.findall(myre, name):
            showinfo(title='错误', message='账号不符合规范')
            return False
        elif not re.findall(myre, secret):
            showinfo(title='错误', message='密码不符合规范')
            return False
        else:
            return True

    def closeWindow(self):
        ans = askyesno(title="提示", message="确定要退出？")
        if ans:
            self.tcpCliSock.close()
            self.root.destroy()
        else:
            pass

def main():
    tcpClintSock.connect(ADDR)
    root = Tk()
    root.title("Let's chat")
    root.iconbitmap("chat-icon.ico")
    root.resizable(0, 0) # 禁止调整窗口大小
    LoginPage(root, tcpClintSock)
    root.mainloop()

if __name__ == '__main__':
    main()



