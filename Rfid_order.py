#Rfid读写模块通讯方式串口通讯
#校验方式：crc16，起始0x0000，截至0x0000，多项式8005
#本程序包含:crc校验、命令解析（十六进制字符串截取）、串口通讯控制
import sys
import binascii
import  crcmod
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
    def __init__(self):
        self.data

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

    #读标签(user数据)，解析接受字符串，返回接受到的数据(根据帧中数据长度数据，截取字符串)
    def analyze_data(self ,text):
        #提取第二、三字节保留着数据长度信息
        len = int(text[2:5] , 16)
        #根据len长度读取data
        data = text[1:2]

    #扫描，解析接受字符串，返回扫描读取到的标签id
    def analyze_read(self , text):
        len = int(text[2:5], 16)
        # 根据len长度读取data
        data = text[1:2]

    def crc16(text):
        he = binascii.unhexlify(text)
        crc32_func = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False, xorOut=0x0000)
        return hex(crc32_func(he))

