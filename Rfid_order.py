#Rfid读写模块通讯方式串口通讯
#校验方式：crc16，起始0x0000，截至0x0000，多项式8005
#本程序包含:crc校验、命令解析（十六进制字符串截取）、串口通讯控制
import sys
import binascii
import  crcmod
import serial
import time
from queue import Queue,LifoQueue,PriorityQueue
from threading import Thread
# crcmod模块使用注意事项：rfid所有通讯以十六进制进行通讯，使用binascii将字符转转化为十六进制先，在传入crcmod计算校验码
rfid_order = {'开始扫描':''}
a = "0002"
print(int(a , 16))
class Rfid():
    #记录操作过的标签
    aerial_1 = []
    aerial_2 = []
    #记录所有通讯信息
    daily = {}
    #通讯相关变量
    order_list = Queue(maxsize=32)
    def __init__(self , rfid_com):
        self.com = rfid_com


    #rfid初始化
    def init(self):
        self.order_list.put('55 00 02 D2 00 EC 24')
        self.order_list.put('55 00 03 62 91 00 5D A2')
        self.order_list.put('55 00 03 62 20 00 FB AB')
        self.order_list.put('55 00 03 62 21 00 7D AB')
        self.order_list.put('55 00 03 62 14 00 C3 AB')
        self.order_list.put('55 00 03 62 18 00 EB AB')
        self.order_list.put('55 00 03 64 30 00 1B D3 26')
        self.order_list.put('55 00 03 62 69 00 4D AE')
        self.order_list.put('55 00 03 62 14 00 C3 AB')
        self.order_list.put('55 00 03 62 18 00 EB AB')
        self.order_list.put('55 00 03 62 21 00 7D AB')
        self.order_list.put('55 00 03 62 23 00 F1 A8')
        self.order_list.put('55 00 03 62 2C 00 D3 A8')
        self.order_list.put('55 00 03 62 15 00 45 A8')
        self.order_list.put('55 00 03 62 15 00 45 A8')
        self.order_list.put('55 00 03 62 69 00 4D AE')
        return self.order_list

    #开始扫描，扫描天线1，2口
    def start_scan(self):
        self.order_list.put('55 00 10 F0 83 01 01 03 00 04 00 00 00 00 00 00 01 08 00 CD 27')
        return self.order_list
    #发送命令线程
    def send_order(self,text):
        if (self.com.isOpen() == True):
            t = '\b\r' + text +'\n'
            send_bytes = self.com.write(t.encode('utf-8'))
            print(send_bytes)

    def deal(self):
        try:
            while(self.order_list.empty() == False):
                time.sleep(0.1)
                print(self.com.isOpen())
                self.send_order(self.order_list.get())
            print('命令执行完成')
        except Exception as e:
            print(str(e))
    #合成命令，选择标签、读标签、写标签时使用
    def mix_order(self , text):
        #帧头：55 ； 数据长度：text的字节数； crc校验码
        return 1
    #清空数据，初始化，进行一个新的流程
    def clear(self):
        self.aerial_1.clear()
        self.aerial_2.clear()
        #将日志数据写入本地，然后清空
        self.daily.clear()

    #根据发送数据，生成要发送的帧（添加校验码和55帧头）
    def produce_frame(self , text):
        #判断text头是否是55，若不是生成crc校验码并在帧头加上55（是否还需加上数据长度待查阅文档后确定）
        if text[0:2] == '55':
            #去除55帧头和长度，生成校验码
            order = text[5:]
            crc = self.crc16(order)
            order = text + crc
            return order
        else:
            crc = self.crc16(text)
            len = int(len(text) , 16)
            order = '55' + str(len) + text + crc
            return order

    #标签操作(选择标签、读标签、写标签)
    def select_tag(self , tag_id):
        frame_head = '55 00 10 80 01 00 60'    #字符串里要不要有空格？？？？
        frame = frame_head + tag_id
        send_frame = self.produce_frame(frame)
        #将选择标签id写入daily列表
        return  send_frame
    def write_tag(self , text):
        #生成命令帧
        frame_head = '55 00 0c 85 02 00 00 00 00 00 02'  # 字符串里要不要有空格？？？？
        frame = frame_head + text
        send_frame = self.produce_frame(frame)
        self.produce_frame()
        #将写入内容存入adaily列表
    def read_tag(self , tag_id):
        # 生成命令帧
        frame_head = '55 00 08 84 02 00 00 00 00 00 04'  # 字符串里要不要有空格？？？？
        send_frame = self.produce_frame(frame_head)
        self.produce_frame()

    #读标签(user数据)，解析接受字符串，返回接受到的数据(根据帧中数据长度数据，截取字符串)
    def analyze_data(text):
        #提取第二、三字节保留着数据长度信息
        len = int(text[2:5] , 16)
        #根据len长度读取data
        if len<8:
            return False
        else:
            data = text[12:28]
            #将解析出来的数据存入daily列表


    #扫描，解析接受字符串，返回扫描读取到的标签id
    def analyze_read(text):
        len = int(text[2:5], 16)
        #从返回数据（16进制）的第9字节开始，读取12字节数据
        if len<12:
            return False
        else:
            rfid_id = text[16:30]
            # 将解析出来的标签id存入aerial_1,daily列表
            return rfid_id


    def crc16(text):
        he = binascii.unhexlify(text)
        crc32_func = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False, xorOut=0x0000)
        return hex(crc32_func(he))
