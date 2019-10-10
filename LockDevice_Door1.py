#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !
"""
Are you OK?
"""

import threading
import serial
import serial.tools.list_ports
import os
import time

OPEN_DOOR_STATUS = b'd1d1d1d1d1d1d1d1d1d1'  # 关闭状态
DELAY_CLOSE_DOOR_TIME_LONG = 1   # 延时时长
DELAY_CLOSE_DOOR_TIME_SHORT = 0

class LockDevice(threading.Thread):
    isOpenLock = False  # 是否打开锁
    isOpenedDoor = False  # 是否打开门
    isWaitingCloseLock = False  # 是否等待上锁
    isUploadImageFlag = False  # 是否upload上锁
    delayCloseLockTime = 0  # 等待上锁的时长
    startStayCloseLock = 0  # 开始等待上锁的时间
    closeLockFlag = 0  # 关门上锁自检测——标记
    
    def __init__(self, deviceName, port):
        super(LockDevice, self).__init__()
        self.deviceName = deviceName
        self.port = port
        
        self.device = self.openDevice(deviceName, port)


    # 打开串口设备
    def openDevice(self, deviceName, port):
        port_list = list(serial.tools.list_ports.comports())

        for i in range(0, len(port_list)):
            print(port_list[i])

        # 打开设备
        device = serial.Serial(deviceName, port, timeout=3)
        print(device.name)

        self.closeLock(device)
        # print(device.read(160))
        return device

    # 开锁
    def openLock(self, device):
        command = [0x63, 0x31]
        device.write(serial.to_bytes(command))
        device.flush()

        self.isOpenLock = True
        
        print("............................... 开门了  ...")
    # 关锁
    def closeLock(self, device):
        command = [0x63, 0x30]
        device.write(serial.to_bytes(command))
        device.flush()

        self.isOpenLock = False
        print("............................... 关门了 ...")

    # 查看门的状态
    def doorStatus(self, device):
        status = device.read(64)
        return status

    # 重新打开串口设备
    def reopenDevice(self):
        try:
            if self.device:
                self.device.close()

            self.device = self.openDevice(self.deviceName, self.port)
        except Exception as e:
            print(e)
            os.system('shutdown -r -t 3')

    # 开启监听门状态
    def run(self):

        # 循环监听数据和状态消息
        while True:
            try:
                # 监听门的状态
                self.lockStatus(self.device)
            except Exception:
                print("########################## 串口异常 ##########################")
                self.reopenDevice()

    # 判断是否开门
    def isOpenDoor(self, status):

        # 门打开 如果包含子字符串返回开始的索引值，否则返回-1。
        if status.find(OPEN_DOOR_STATUS) != -1:
            print("门已经打开...")
            # 门已经打开标记
            self.isOpenedDoor = True
            self.isWaitingCloseLock = False
            self.closeLockFlag = 0 # 关闭门自检测——清零

        else:  # 门关闭
            print("门已经关闭...")
            # 门已经关闭标记
            self.isOpenedDoor = False

            # 延时关门逻辑处理
            if self.isOpenLock and not self.isWaitingCloseLock:
                self.isWaitingCloseLock = True
                self.closeLockFlag = 0

                # 门关上的时间
                self.startStayCloseLock = time.time()

                # 没有打开过门时，等待10s;打开过门时，等待5s
                if not self.isOpenedDoor:
                    self.delayCloseLockTime = DELAY_CLOSE_DOOR_TIME_LONG
                else:
                    self.delayCloseLockTime = DELAY_CLOSE_DOOR_TIME_SHORT
            else:
                # 关闭门自检测，累积
                self.closeLockFlag += 1

            # 轮询关锁命令
            if self.closeLockFlag > 10:
                self.closeLockFlag = 0
                self.closeLock(self.device)



            # 延时开锁时长
        if self.isWaitingCloseLock:
            current_time = time.time()

            if current_time - self.startStayCloseLock >= self.delayCloseLockTime:
                print("锁已经关上，开始上传图片...是否需要上传图片# 延时【%d】  2:上传图片# 5:上传图片" % self.delayCloseLockTime)

                self.startStayCloseLock = current_time
                self.isWaitingCloseLock = False
                # 关锁
                self.closeLock(self.device)

                # 5#当开过门后，才上传本地图片
                if self.delayCloseLockTime == DELAY_CLOSE_DOOR_TIME_SHORT:
                    # 上传本地图片
                    self.isUploadImageFlag = True

    # 查看锁的状态
    def lockStatus(self, device):

        status = self.doorStatus(device)
        print("DOOR_STATUS#", status)

        if status == b"":
            os.system('shutdown -r -t 3')

        # 控制板异常情况下，重启设备
        if status.find(b"`0`0`0`0`0`0") != -1:
            os.system('shutdown -r -t 3')

        # 判断锁的状态
        self.isOpenDoor(status)


if __name__ == "__main__":
    thread = LockDevice("com", 9600)
    thread.start()
