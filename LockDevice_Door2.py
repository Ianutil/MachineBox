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

CLOSE_DOOR_STATUS = "FE020102105D"  # 关闭状态
OPEN_DOOR_STATUS = "FE020100919C"  # 关闭状态
DELAY_CLOSE_DOOR_TIME_LONG = 1   # 延时时长
DELAY_CLOSE_DOOR_TIME_SHORT = 0

class LockDevice(threading.Thread):
    isOpenLock = False  # 是否打开锁
    isOpenedDoor = False  # 是否打开门
    isWaitingCloseLock = False  # 是否等待上锁
    isUploadImageFlag = False  # 是否upload上锁
    delayCloseLockTime = 0  # 等待上锁的时长
    startStayCloseLock = 0  # 开始等待上锁的时间
    closeLockFlag = 0  # 上锁

    noStatusCount = 0   # 未获得检测状态的次数

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

        # 打开第一次时，先关闭锁
        self.closeLock(device)

        # print(device.read(160))
        return device

    # 开锁
    def openLock(self, device):
        command = [0xFE, 0x05, 0x00, 0x00, 0xFF, 0x00, 0x98, 0x35]
        device.write(serial.to_bytes(command))
        device.flush()
        result = device.read(8).hex().upper()
        print(result)

        self.isOpenLock = True
        
        print("............................... 开门了  ...")
    # 关锁
    def closeLock(self, device):
        command = [0xFE, 0x05, 0x00, 0x00, 0x00, 0x00, 0xD9, 0xC5]
        device.write(serial.to_bytes(command))
        device.flush()
        result = device.read(8).hex().upper()
        print(result)

        retryTime = 0
        while result == "" and retryTime < 10:
            retryTime += 1
            device.write(serial.to_bytes(command))
            device.flush()
            result = device.read(8).hex().upper()
            print(result, "关门次数---", retryTime)

        # 开启重启模式
        if retryTime >= 10:
            self.reopenDevice()

        self.isOpenLock = False
        print("............................... 关门了 ...")

    # 查看门的状态
    def doorStatus(self, device):
        # FE 02 00 00 00 04 6D C6
        command = [0xFE, 0x02, 0x00, 0x00, 0x00, 0x04, 0x6D, 0xC6]
        device.write(command)
        device.flush()
        status = device.read(6).hex().upper()
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
        start_time = 0
        # 循环监听数据和状态消息
        while True:
            try:

                # 设备异常检测
                if self.noStatusCount > 10:
                    self.reopenDevice()
                current_time = time.time()
                # 每10秒钟，请求一次锁的状态
                if current_time - start_time > 2:
                    start_time = current_time
                    # 监听门的状态
                    self.lockStatus(self.device)
            except Exception as e:
                print("########################## 串口异常 ##########################")
                print(e)
                self.reopenDevice()

    # 判断是否开门
    def isOpenDoor(self, status):

        # 门关闭
        if status == CLOSE_DOOR_STATUS:
            print("门已经关闭...")
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

            # 门已经关闭标记
            self.isOpenedDoor = False

        elif status == OPEN_DOOR_STATUS:  # 门打开
            print("门已经打开...")
            # 门已经打开标记
            self.isOpenedDoor = True
            self.isWaitingCloseLock = False
            self.closeLockFlag = 0  # 关闭门自检测——清零


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

        if status == "" or status == "000000000000":
            self.noStatusCount += 1
            print("获取锁状态------", self.noStatusCount)
            return

        self.noStatusCount = 0

        # 判断锁的状态
        self.isOpenDoor(status)


if __name__ == "__main__":
    thread = LockDevice("com", 9600)
    thread.start()
