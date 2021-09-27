#创建日期2021-08-31
#主要功能：[角度x，角度y，距离]+[已知x，已知y，已知z](目标点) 计算转换全站仪[x,y,z]
#全站仪[x，y，z]+[估计x，估计y，估计z](目标点) 计算转换全站仪需要旋转的量[det_x,det_y]
#描述：两性工作：1.根据已知点加全站仪扫描获取的角度距离数据计算全站仪当前位置坐标；2.在大致了解全站仪位置及反光贴位置计算一个旋转量，减少扫描时间。
#注：全站仪坐标系建立（未确定），全站仪指向正前方时坐标点设定（未确定）。会影响整体坐标计算
import math
import re

class station:
    #从全站仪返回的数据中提取处[角度x，角度y，距离]
    def get_angle_from_com_response(self ,response):
        response_str = re.split(':|,', response)[2:]
        #print(response_str)
        #print(response_str[0])
        try:
            asd = int(response_str[0])

            if asd == 0:
                point = [response_str[1], response_str[2], response_str[3]]
                return point
                # horizontal = float(response_str[1])
                # vertical = float(response_str[2])
                # dist = float(response_str[3])
                # trans_position(horizontal, vertical, dist)
        except:
            return False

    #每次扫描照准后，全站仪返回对准正前方[0,0,z]
    def recover(x,y,z):
        s=[]

    #由全站仪到一位置确定的反光片的角度距离计算全站仪位置
    def getNEZ(he, ve, dist):
        north = dist * math.cos(math.pi / 2 - ve) * math.cos(he)

        eastern = dist * math.cos(math.pi / 2 - ve) * math.sin(he)
        height = dist * math.sin(math.pi / 2 - ve)

        return float('%.4f' % north), float('%.4f' % eastern), float('%.4f' % height)

    #计算全站仪到目标反光片的det_X,det_y,det_z.参数p（目标反光片的坐标），mear(全站仪照准时的角度距离数据)
    def get_det(p , mear):
        det_x = mear[2] * math.cos(math.pi / 2 - mear[1]) * math.cos(mear[0])
        det_y = mear[2] * math.cos(math.pi / 2 - mear[1]) * math.sin(mear[0])
        det_z = mear[2] * math.sin(math.pi / 2 - mear[1])
        #det_z = math.sqrt( pow(mear[2],2) / (pow(math.tan(mear[0]),2) + pow(math.tan(mear[1]),2) + 1) )
        #det_x = math.tan(mear[0]) * det_z
        #det_y = math.tan(mear[1]) * det_z
        res = [float('%.4f' % det_x), float('%.4f' % det_y), float('%.4f' % det_z)]
        return res

    #det_X,det_y,det_z计算全站仪位置坐标.det_p（全站仪到目标反光片的相对坐标差），p（目标反光片坐标）
    def get_point(det_p,p):
        res = []
        res[0] = p[0] + det_p[0]
        res[1] = p[1] + det_p[1]
        res[2] = p[2] + det_p[2]
        return res

    #由全站仪当前位置和一个待确定但大致知道位置的反光片坐标计算旋转角度,p(全站仪坐标)，p1（目标点坐标)
    def get_angle(p,p1):
        det = []
        det[0] = p1[0] - p[0]
        det[1] = p1[1] - p[1]
        det[2] = p1[2] - p[2]
        angle_x = math.atan(det[0]/det[2])
        angle_y = math.atan(det[0] / det[2])
        return

    #输入一个基准点坐标参数和角度距离参数，计算返回全站仪坐标
    def caclu_station(self , point,vector):
        temp_det = self.get_det(point , vector)
        temp_point = self.get_point(temp_det , point)
        return temp_point
        #输入全站仪坐标和一个vector计算反光片坐标
    def caclu_point(self ,point , vector):
        temp_det = self.get_det(point, vector)
        res = []
        res[0] = point[0] - temp_det[0]
        res[1] = point[1] - temp_det[1]
        res[2] = point[2] - temp_det[2]
        return res
    #计算旋转角度
    def caclu_angle(self,point , sta_point):
        detx = point[0] - sta_point[0]
        dety = point[1] - sta_point[1]
        detz = point[2] - sta_point[2]