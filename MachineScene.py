#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !
"""
Are you OK?
"""
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import requests

DELAY_TIME = 30 * 1000

data = [
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409683785&di=adb4e7518afef91c3c55f35465e67a16&imgtype=0&src=http%3A%2F%2Fp3.so.qhmsg.com%2Ft01b9aeb9e668612fe8.jpg",
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409683785&di=d39fe193f3de6878c4ae8c67be193bee&imgtype=0&src=http%3A%2F%2Fk.zol-img.com.cn%2Fdcbbs%2F18638%2Fa18637891_01000.jpg",
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409683784&di=c03d43993824e1354025e77054df1e0b&imgtype=0&src=http%3A%2F%2Fqcloud.dpfile.com%2Fpc%2Fjkd4h0VSCZrbUq5s6Rpv_05bcc0DUxa-BOWpibQOZJSjcwneCSkM4oB7pN8EPXlzTK-l1dfmC-sNXFHV2eRvcw.jpg",
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409683784&di=ea217c52900399920c6905230640566f&imgtype=0&src=http%3A%2F%2Fi5.hexunimg.cn%2F2014-11-20%2F170616282.jpg",
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409834777&di=6330dfa7d75a8563cc216b1daa032b70&imgtype=0&src=http%3A%2F%2Fwww.591wed.com%2Fupimages%2F112751408002618.jpg",
    "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1558409859187&di=a6dd5d589ece4f6a2ca84983dbb7e8c9&imgtype=0&src=http%3A%2F%2Fqcloud.dpfile.com%2Fpc%2FV8PNbb7Bow3hvkEREQ0Y9UQH9VaBAoMW2eDkQS2MWEGjpO0oDC1nRw8deAzYxv-zTYGVDmosZWTLal1WbWRW3A.jpg",
]


class MachineScene(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('屏幕广告')
        self.setWindowIcon(QtGui.QIcon('camera.png'))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.desktop = QtWidgets.QApplication.desktop()

        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        self.height = self.screenRect.height()
        self.width = self.screenRect.width()

        print("Screen Size#", self.width, "x", self.height)

        self.resize(self.height, self.height)

        self.initView()
        self.startTimer()

    def initView(self):
        # 创建窗口主部件
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_widget.setStyleSheet('''
                                           QWidget{
                                           border:none;
                                           background-color:#000000;
                                           margin-bottom:0px;
                                           margin-left:0px;
                                           margin-top:0px;
                                           margin-right:0px;
                                           padding:0px;
                                           }
                                       ''')
        self.createScene()

        # 行号，列号，行宽，列宽
        self.main_layout.addWidget(self.scene_widget, 0, 0, 1, 1)

        self.setCentralWidget(self.main_widget)

    def createScene(self):
        self.scene_widget = QtWidgets.QWidget()
        self.scene_layout = QtWidgets.QGridLayout()
        self.scene_widget.setLayout(self.scene_layout)

        self.scene_label = QtWidgets.QLabel()

        self.scene_label.setStyleSheet('''
                           QWidget{
                           background-color:#000000;
                           margin-bottom:0px;
                           margin-left:0px;
                           margin-top:0px;
                           margin-right:0px;
                           }
                       ''')

        self.scene_layout.addWidget(self.scene_label, 0, 0, 1, 1)

        self.index = 0
        self.showImage(data[self.index])

    def startTimer(self):
        self.timer = QtCore.QTimer()
        # 定时器结束，触发showTime方法
        self.timer.timeout.connect(self.showNextScene)

        # 设置时间间隔并启动定时器
        self.timer.start(5 * 1000)

    def showImage(self, url):
        req = requests.get(url)
        image = QtGui.QPixmap()
        image.loadFromData(req.content)
        image = image.scaled(self.width, self.height)
        self.scene_label.setPixmap(image)

    def showNextScene(self):
        # 获取系统当前时间
        time = QtCore.QDateTime.currentDateTime()
        # 设置系统时间的显示格式
        timeDisplay = time.toString('yyyy-MM-dd hh:mm:ss dddd')

        print(timeDisplay)

        self.index += 1
        size = len(data)
        print("index#", self.index, " count#", size)

        if self.index >= size:
            self.index = 0

        self.timer.setInterval(DELAY_TIME)
        self.showImage(data[self.index])




def startApp():

    # UI展示
    app = QtWidgets.QApplication(sys.argv)
    window = MachineScene()

    window.show()

    sys.exit(app.exec_())



if __name__ == "__main__":
    print("=============================================")
    print("**************  无人售货柜开始启动  *****************")
    print("=============================================")
    startApp()