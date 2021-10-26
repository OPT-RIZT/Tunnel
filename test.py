import math
import time
import sys
import serial
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from socket import *
from auto_test import *
from queue import Queue,LifoQueue,PriorityQueue
from Point_trans import *


order_dict = {'测量':'%R1Q,50013:2' , '旋转':'%R1Q,50003:0,0,0,0,0,0,0' , '搜索':'%R1Q,9029:0.2618,0.2618,0','查询':'%R1Q,2003:0','旋转1':'%R1Q,50003:0.035,-0.032,0,0,0,0,0 ' ,'旋转2':'%R1Q,50003:0.042,-0.015,0,0,0,0,0' ,'旋转3':'%R1Q,50003:-0.078,0.06,0,0,0,0,0' }
order_list = Queue(maxsize=18)
class MyMainWindow(QMainWindow , Ui_MainWindow , QObject):
    def __init__(self ):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.com = serial.Serial
        self.readflag = False
        self.pushButton.clicked.connect(self.stop)
        self.station_single.connect(self.deal)
        #order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转1'])
        #order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转2'])
        order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转3'])
        self.init()

    def stop(self):
        order_list.queue.clear()
        order_list.put('stop')
    station_single = pyqtSignal(str)
    def ini_order(self):
        #order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转1'])
        #order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转2'])
        #order_list.put(order_dict['查询'])
        #order_list.put(order_dict['搜索'])
        #order_list.put(order_dict['测量'])
        order_list.put(order_dict['旋转3'])
        self.send_ord(order_list.queue[0])
    def send(self):
        self.send_ord(order_dict['查询'])
        print(order_dict['查询'])
    def init(self):
        # 串口通讯，连接全站仪
        try:
            self.com = serial.Serial("COM3", 115200)
            if (self.com.isOpen() == True):
                self.textEdit.append('状态：连接')
                self.readflag = True
                read_s = Thread(target=self.station_recv)
                read_s.start()
            else:
                self.textEdit.append('状态：断开')
        except Exception as e:
            self.textEdit.append(str(e))
            self.readflag = False

    def send_ord(self , text):
        if (self.com.isOpen() == True):
            t = '\b\r' + text +'\n'
            send_bytes = self.com.write(t.encode('utf-8'))
            self.textEdit.append(text+'\r\n' + str(send_bytes))
        else:
            self.plainTextEdit.appendPlainText('先连接串口')

    def station_recv(self):
        time.sleep(0.1)
        while self.readflag:
            if self.com.inWaiting():
                try:
                    # data = self.open_com.read_all().decode("utf-8")
                    data = self.com.readline().decode("utf-8")
                    print("接受：{}".format(data))
                    if len(data) > 5:
                        # print(data.length)
                        self.station_single.emit(str(data))
                except Exception as e:
                    print(str(e))

    def deal(self , text):
        ca = station()
        #print(text)
        try:
            #根据队列命令执行相应分支动作，执行完成删除队列顶部命令，发送队列中下一条命令
            if order_list.queue[0] == order_dict['测量']:
                #返回向量写入txt
                # point11 = ca.get_angle_from_com_response(text)
                # with open("vector.txt", 'a') as fs:
                #     fs.write('(' + point11[0]+ ',' )
                #     fs.write(point11[1] + ',')
                #     fs.write(point11[2] + ')')

                print('测量完成')
            if order_list.queue[0] == order_dict['搜索']:
                #解析返回数据，0：表示成功继续下一条指令，1：表示失败不知道该怎么办
                ss = 1
                print('搜索完成')
            if order_list.queue[0] == order_dict['查询']:
                #在界面上显示信息（当前激光照射位置偏角，和全站仪x-y轴倾斜程度）
                #print(text[9:26])
                #print(text[44:53])
                #print(text[54:63])
                self.lineEdit.setText("角向量：{},x轴倾角：{},y轴倾角：{}".format(text[9:26] , text[44:53] , text[54:63]))
                print("查询完成")
                print(order_list.queue)
                #根据倾角转回起始点（生成命令）

            #旋转不是固定命令，提取命令前几个字符用于判断
            if order_list.queue[0][5:10] == '50003':
                sdas = 0
                print("旋转完成")
            if order_list.queue[0] == 'stop':
                return
            self.textEdit.append(order_list.get())
            if order_list.empty() == True:
                print('命令执行完成')
                with open("vector.txt", 'a') as fs:
                    fs.write('\r\n')
                #从新写命令进队列，再次采集
                self.ini_order()
                return
            self.send_ord(order_list.queue[0])
            self.textEdit.append("发送：{}".format(order_list.queue[0]))
        except Exception as e:
            print(str(e))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec_())