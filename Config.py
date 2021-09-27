#创建日期2021.08.31
#主要功能：读取通讯控制命令、程序运行所需配置参数（贴片时外界环境如温度气压高度）
#实现通过configobj模块读取ini（很少写ini）

from configobj import ConfigObj
import os
import datetime

class ini_operate:
    file_path = os.path.dirname(os.path.abspath(__file__)) + '\conf.ini'
    #命令集合（字典）
    order_dist = dict()
    def __init__(self):
        #检查配置文件是否存在
        if(os.path.exists(self.file_path)):
            self.get_config()
            self.get_transit_order()
            self.get_RFID_order()
            self.get_PLC_order()
            return
        else:
            print(self.file_path)
            config = ConfigObj()
            config.filename = self.file_path
            config['create_time'] = datetime.datetime.now()
            config.write()

    #贴片时的温度，气压，全站仪高度等数据
    def get_config(self):
        temp_ord_dict = dict()
        self.order_dist.update(temp_ord_dict)
    def get_transit_order(self):
        temp_ord_dict = dict()
        self.order_dist.update(temp_ord_dict)
    def get_RFID_order(self):
        temp_ord_dict = dict()
        self.order_dist.update(temp_ord_dict)
    def get_PLC_order(self):
        temp_ord_dict = dict()
        self.order_dist.update(temp_ord_dict)

    #写入贴片时
    def write_ini(self,dict):
        config = ConfigObj(self.file_path, encoding='UTF-8')
        config.write()