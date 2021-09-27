from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from main_window import *
from threading import Thread
from socket import *
from Point_trans import *
import sys
import time
import serial

client = socket()
order_dict = {'查找角度及距离':'%R1Q,50013:2' , '旋转':'%R1Q,50003:0,0,0,0,0,0,0' , '搜索并照准':'%R1Q,9029:0.2618,0.2618,0'}
class MyMainWindow(QMainWindow , Ui_MainWindow , QObject):
    def __init__(self ):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.plc = socket()
        #PLCJ接受数据标志位，启动tcp连接后至True
        self.plc_Flag = False
        self.plc_single.connect(self.plc_recv)
        self.station_com = serial.Serial
        #self.station_order_TPYR
        self.station_single.connect(self.station_recv)
        self.rfid = serial.Serial
        self.pushButton_3.clicked.connect(self.connect_tcp)
        #软件启动，自检并完成tcp，全站仪串口，rfid串口连接
        self.init()
        #信号槽连接
        self.radioButton.clicked.connect(self.io_change)
        self.station_single.connect(self.send_ord)
        #暂时将界面上全站仪部分的连接按钮做发送命令使用
        self.pushButton.clicked.conncet(self.re)

    deal = QThread()
    def io_change(self):
        s =1

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
                read_s = Thread(target=self.station_recv)
                read_s.start()
            else:
                self.label.setText('状态：断开')
        except Exception as e:
            self.textEdit.append(str(e))

    def connect_tcp(self):
        #待定按钮的任务，暂时没有
        s = 1
    def tcp_recv(self):
        time.sleep(0.1)
        while True:
            if (self.plc_Flag):
                data = self.plc.recv(1024)
                if (data.__len__() > 0):
                    self.plc_single.emit(str(data))
                    print("recv:>", data.decode())
                else:
                    continue
            else:
                continue
    def plc_recv(self,str):
        self.textEdit_3.append(str)

    #串口(全站仪)接受数据函数
    def station_recv(self):
        time.sleep(0.1)
        while self.readflag:
            if self.com1.inWaiting():
                try:
                    # data = self.open_com.read_all().decode("utf-8")
                    data = self.com1.readline().decode("utf-8")
                    print(len(data))
                    if len(data) > 10:
                        # print(data.length)
                        self.station_single.emit(str(data))
                        print(data)
                except Exception as e:
                    print(str(e))
    def station_data_deal(self,str):
        tran = station()
        #接受数据解析出角度距离数据
        get_vector = tran.get_angle_from_com_response(str)
        #测试流程，根据列表point_list数据个数确定当前反光贴是那个（需加上判断，向左还是向右）

        #根据基准点计算全站仪坐标

        #根据角度（朝向左侧还是右侧，确定基准点（rfid上一组读取的两个点））
        #计算全站仪坐标
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
        self.re(order_dict['查找角度及距离'])
    def move(self):
        ff = station()
        ff.get_angle(self.station_point , self.basepoint)
    def re(self , text):
        if (self.com1.isOpen() == True):
            t = '\b\r' + text +'\n'
            send_bytes = self.com1.write(t.encode('utf-8'))
            self.plainTextEdit.appendPlainText(self.send_text.text()+'\r\n' + str(send_bytes))
            ord = re.split(':|,', text)[1]
            self.send_list.append(ord)
        else:
            self.plainTextEdit.appendPlainText('先连接串口')
    test = Thread()
    def send_ord(self,str):
        print(str)
        self.test = Thread(target=self.get3point)
        self.test.start()
    def get3point(self):
        ca = station()
        self.get_angle = ca.get_angle_from_com_response()
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