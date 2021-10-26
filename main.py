from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from main_window import *
from threading import Thread
from socket import *
from Point_trans import *
import sys
import time
import binascii
import serial
import Rfid_order
from queue import Queue,LifoQueue,PriorityQueue

client = socket()
order_dict = {'停止':'%R1Q,6002.0','测量':'%R1Q,50013:2' , '旋转':'%R1Q,50003:0,0,0,0,0,0,0' , '搜索':'%R1Q,9029:0.2618,0.2618,0','查询':'%R1Q,2003:0','旋转1':'%R1Q,50003:0.035,-0.032,0,0,0,0,0' ,'旋转2':'%R1Q,50003:0.042,-0.015,0,0,0,0,0' ,'旋转3':'%R1Q,50003:-0.078,0.06,0,0,0,0,0' }
class MyMainWindow(QMainWindow , Ui_MainWindow , QObject):
    def __init__(self ):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.plc = socket()
        #PLCJ接受数据标志位，启动tcp连接后至True
        self.plc_Flag = False
        self.plc_single.connect(self.plc_recv)
        self.order_rfid = Queue(maxsize=32)
        self.order_station = Queue(maxsize=32)
        self.rfid_com = serial.Serial
        self.rfid_class = Rfid_order.Rfid(self.rfid_com)
        self.rfid_single.connect(self.get_rfid_data)
        #self.station_order_TPYR
        self.station_com = serial.Serial
        self.station_single.connect(self.station_data_deal)
        self.pushButton_3.clicked.connect(self.connect_tcp)


        #信号槽连接
        self.radioButton.clicked.connect(self.io_change)
        self.station_single.connect(self.station_data_deal)
        #暂时将界面上全站仪部分的连接按钮做发送命令使用
        self.pushButton.clicked.connect(self.re)
        start_ini = Thread(target=self.start)
        start_ini.start()

    deal = QThread()

    def io_change(self):
        s =1
    def start(self):
        time.sleep(1)
        #软件启动，自检并完成tcp，全站仪串口，rfid串口连接
        self.init()
    #接受通讯返回的信号，在窗口textedit显示
    plc_single = pyqtSignal(str)
    station_single = pyqtSignal(str)
    rfid_single = pyqtSignal(str)
    def init(self):
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #启动窗口后，检查个部分状态，自动连接通讯串口，网口，读取通讯命令
        try:
            #当前代码地址是乱写的，以后确定。时间2021-09-01
            self.plc.connect(('127.0.0.1',5000))
            self.plc_single.emit('连接成功')
            self.label_8.setText('已连接')
            self.plc_Flag = True
            read_t = Thread(target=self.tcp_recv)
            read_t.start()
        except Exception as e:
            self.plc_single.emit(str(e))
         #串口通讯，连接全站仪
        try:
            self.station_com = serial.Serial("COM3", 115200)
            if (self.station_com.isOpen() == True):
                self.label.setText('状态：连接')
                self.station_flag = True
                read_s = Thread(target=self.station_recv)
                read_s.start()
            else:
                self.label.setText('状态：断开')
        except Exception as e:
            self.textEdit.append(str(e))
        # rfid通讯
        try:
            self.rfid_com = serial.Serial("COM6", 115200)
            if (self.rfid_com.isOpen() == True):
                self.label_4.setText('状态：连接')
                self.rfid_flag = True
                read_r = Thread(target=self.rfid_recv)
                read_r.start()
                self.order_rfid = self.rfid_class.init()
                self.order_rfid.put('55 00 10 F0 83 01 01 03 00 04 00 00 00 00 00 00 01 08 00 CD 27')
                print(self.order_rfid.queue)
                time.sleep(0.2)
                rfid_send = Thread(target= self.deal_rfid)
                rfid_send.start()
            else:
                self.label_4.setText('状态：断开')
        except Exception as e:
            self.textEdit_2.append(str(e))

    def connect_tcp(self):
        #待定按钮的任务，暂时没有
        s = 1
    def tcp_recv(self):
        time.sleep(0.1)
        while True:
            if (self.plc_Flag):
                data_t = self.plc.recv(1024)
                if (data_t.__len__() > 0):
                    self.plc_single.emit(str(data_t))
                    print("recv:>", data_t.decode())
                else:
                    continue
            else:
                continue

    #接受到tcp传送过来的命令，执行相应操作（计算距离，或者贴片）
    def plc_recv(self,str):
        self.textEdit_3.append(str)

    #串口(全站仪)接受数据函数
    def station_recv(self):
        time.sleep(0.1)
        while self.station_flag:
            if self.station_com.inWaiting():
                print(55)
                try:
                    # data = self.open_com.read_all().decode("utf-8")
                    data_s = self.station_com.readline().decode("utf-8")
                    print(len(data_s))
                    if len(data_s) > 10:
                        # print(data.length)
                        self.station_single.emit(str(data_s))
                        print(data_s)
                except Exception as e:
                    print(str(e))
    point_list = []
    leng_point = []
    def station_data_deal(self,str):
        ca = station()
        # print(text)发觉脑子是不够用了，社会不是那么好混的，但是相信我自己再也不会自备，我没自己想的那么不堪也不是什么牛逼的人。
        #学着和自己相处，认识自己。与他人交流时多考虑下他人感受，不要太自我
        if len(self.order_station.queue) == 0:
            return
        try:
            # 根据队列命令执行相应分支动作，执行完成删除队列顶部命令，发送队列中下一条命令
            if self.order_station.queue[0] == order_dict['测量']:
                # 返回向量写入txt
                point11 = ca.get_angle_from_com_response(str)
                with open("vector.txt", 'a') as fs:
                    fs.write('(' + point11[0] + ',')
                    fs.write(point11[1] + ',')
                    fs.write(point11[2] + ')')

                print('测量完成')
                self.point_list.append(point11)
                #计算旋转量，转回初始值
                #删除当前队列值
                #发送旋转命令
                if len(self.point_list) > 3:
                    #计算当前全站仪位置
                    p = (1,2,3)
                    if len(self.leng_point) > 0:
                        juli = p - self.leng_point[-1]#详细计算不是两点相减，是计算距离
                        #界面刷新显示label_5显示， label_12显示计算了多少次
                    self.leng_point.append(p)

            if self.order_station.queue[0] == order_dict['搜索']:
                # 解析返回数据，0：表示成功继续下一条指令，1：表示失败不知道该怎么办
                ss = 1
                print('搜索完成')
            if self.order_station.queue[0] == order_dict['查询']:
                # 在界面上显示信息（当前激光照射位置偏角，和全站仪x-y轴倾斜程度）
                # print(text[9:26])
                # print(text[44:53])
                # print(text[54:63])
                print(str)
                self.label_11.setText('倾角：{}，{}'.format(str[44:53], str[54:63]))
                #self.lineEdit.setText("角向量：{},x轴倾角：{},y轴倾角：{}".format(str[9:26], str[44:53], str[54:63]))
                print("查询完成")
            # 旋转不是固定命令，提取命令前几个字符用于判断
            if self.order_station.queue[0][5:10] == '50003':
                sdas = 0
                print("旋转完成")
            if self.order_station.queue[0] == 'stop':
                return
            self.textEdit.append(self.order_station.get())
            if self.order_station.empty() == True:
                print('命令执行完成')
                with open("vector.txt", 'a') as fs:
                    fs.write('\r\n')
                # 从新写命令进队列，再次采集
                self.ini_order()
                return
            self.send_order(self.order_station.queue[0],0)
            self.textEdit.append("发送：{}".format(self.order_station.queue[0]))
        except Exception as e:
            print(str(e))
        #接受数据解析出角度距离数据
        get_vector = ca.get_angle_from_com_response(str)
        #测试流程，根据列表point_list数据个数确定当前反光贴是那个（需加上判断，向左还是向右）

        #根据基准点计算全站仪坐标

        #根据角度（朝向左侧还是右侧，确定基准点（rfid上一组读取的两个点））
        #计算全站仪坐标

    def rfid_recv(self):
        time.sleep(0.1)
        while self.rfid_flag:
            if self.rfid_com.inWaiting():
                try:
                    data_r = self.rfid_com.read_all()
                    self.rfid_single.emit(str(data_r))
                    print(str(data_r))
                except Exception as e:
                    print(str(e))

    def deal_rfid(self):
        print(self.order_rfid.queue)
        try:
            while(self.order_rfid.empty() == False):
                time.sleep(0.5)
                self.send_order(self.order_rfid.get() , 1)
            print('命令执行完成')
        except Exception as e:
            print(str(e))
    def get_rfid_data(self , text):
        self.textEdit_2.append(text)
    #发送串口命令函数（rfid，全站仪二合一，用参数type区分）
    def send_order(self , text , ty):
        #发送全站仪命令，发送数据类型为字符串utf-8;
        if(ty == 0):
            if (self.station_com.isOpen() == True):
                t = '\b\r' + text +'\n'
                send_bytes = self.station_com.write(t.encode('utf-8'))
                #self.textEdit.appendPlainText(self.send_text.text()+'\r\n' + str(send_bytes))
            else:
                self.textEdit.appendPlainText('先连接串口')
        #发送rfid命令,serial只能字符串发送，读写模块所需命令为16进制hex类型，故先将16进制字符串去空格，转化为（\01\ea形式）十六进制字符串，以utf-8形式发送
        else:
            if (self.rfid_com.isOpen() == True):
                text = text.replace(' ' , '')
                t = binascii.unhexlify(str.encode(text))
                #t = text.encode('hex')
                send_bytes = self.rfid_com.write(t)
            else:
                self.textEdit_2.appendPlainText(self.send_text.text() + '\r\n' + str(text))

    base_point1 = [0,0,0]
    base_point2 = [-1, 0, 0]
    base_point3 = [1, 0, 0]
    basepoint = []
    get_angle = []
    station_point=[]
    point_list = []
    def write_txt(self):
        with open("dat.txt" , 'w') as fs:
            fs.write(self.base_point1 + ',')
            fs.write(self.base_point2 + ',')
            fs.write(self.base_point3 + ',')
    def write_txt_point(self):
        with open("dat.txt", 'w') as fs:
            fs.writelines(self.point_list)
            self.point_list.clear()

    #测试使用
    def anl(self):
        self.re(order_dict['测量'])
    def move(self):
        ff = station()
        ff.get_angle(self.station_point , self.basepoint)
    def re(self , text):
        self.order_station.put(order_dict['查询'])
        # order_list.put(order_dict['搜索'])
        #order_station.put(order_dict['测量'])
        self.order_station.put(order_dict['旋转1'])
        self.order_station.put(order_dict['查询'])
        # order_list.put(order_dict['搜索'])
        self.order_station.put(order_dict['测量'])
        self.order_station.put(order_dict['旋转2'])
        self.order_station.put(order_dict['查询'])
        # order_list.put(order_dict['搜索'])
        #order_station.put(order_dict['测量'])
        self.order_station.put(order_dict['旋转3'])
        self.send_order(self.order_station.get() , 0)
    test = Thread()
    def send_ord(self,str):
        print(str)
        self.test = Thread(target=self.get3point)
        self.test.start()
    def get3point(self):
        ca = station()
        #self.get_angle = ca.get_angle_from_com_response()
        print(self.get_angle)
        #手动转全站仪至第一个点
        if(len(self.point_list)) == 0:
            #计算全站仪坐标
            self.station_point = ca.caclu_station(self.base_point1 , self.get_angle)
            self.point_list.__add__(self.base_point1)
            #旋转至第二个点附近

        if(len(self.point_list)) == 1:
            #由全站仪计算反光片坐标
            temp_point = ca.caclu_point(self.get_angle , self.station_point)
            self.point_list.__add__(temp_point)
            #旋转至第三个点附近

        if (len(self.point_list)) == 2:
            # 由全站仪计算反光片坐标
            temp_point = ca.caclu_point(self.get_angle, self.station_point)
            self.point_list.__add__(temp_point)
            # 数据写入txt，并清除point_list
            self.write_txt_point()
        self.test.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec_())