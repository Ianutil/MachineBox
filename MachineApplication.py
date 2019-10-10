#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !
import LockDevice_Door1, LockDevice_Door2, UploadMachineImage
import time
import requests
import json


DEVICE_ID = "890" # 设备ID
DEVICE_NAME = 'COM12'  # 串口设备
DEVICE_PORT = 9600  # 串口设备端口号

DEVICE_TYPE = 2 # 1:控制板；2:集电器

class MachineApplication(object):
    # 打开设备的用户信息
    user_data_info = {}

    def __init__(self):
        super().__init__()

    # 查看锁的状态
    def requestLockStatus(self, device, deviceId):
        url = "https://sss.bailianic.com/front/wx/lock/status?deviceId=" + deviceId
        print("Request#url=%s" % url)
        req = requests.get(url=url)

        print("Response#%s" % req.text)

        if req.status_code == 200:
            data = json.loads(req.text)

            try:
                print("********************是否开门#", data["data"]["open"])

                if data["data"]["open"]:
                    self.user_data_info = data["data"]
                    device.openLock(device=device.device)
                    self.requestCloseLock(orderId=data["data"]["id"])

                    # deviceStatus#0:查询；1：补货；2：客户
                if data["data"]["deviceStatus"] == 0:
                    # door_status#1:表示开门;2:表示关门
                    door_status = 1 if device.isOpenedDoor else 2
                    print("door_status#%d" % door_status)
                    UploadMachineImage.upload_camera_image(deviceId, door_status)

            except Exception as e:
                print("请求服务器开锁命令失败")
                print(e)

    # 关闭锁
    def requestCloseLock(self, orderId):
        try:
            url = "https://sss.bailianic.com/front/wx/lock/close?orderId=" + orderId
            print("Request#url=%s" % url)

            req = requests.post(url=url)

            print("Response#%s" % req.text)

            if req.status_code == 200:
                data = json.loads(req.text)
                print(data)
        except Exception as e:
            print("请求服务器关门失败")
            print(e)

    # 开启设备主函数
    def startMachineBox(self):

        # 根据设备类型，进行选择不同的版本控制器
        if DEVICE_TYPE == 1:
            self.device = LockDevice_Door1.LockDevice(DEVICE_NAME, DEVICE_PORT)
        elif DEVICE_TYPE == 2:
            self.device = LockDevice_Door2.LockDevice(DEVICE_NAME, DEVICE_PORT)

        # 启动监听任务
        self.device.start()

        start_time = 0
        # 循环监听数据和状态消息
        while True:

            if self.device.isUploadImageFlag:
                # 上传柜子信息关闭
                self.device.isUploadImageFlag = False
                try:
                    # 上传本地图片
                    UploadMachineImage.save_camera_image(self.user_data_info["deviceId"],
                                                         self.user_data_info["wxOpenId"],
                                                         self.user_data_info["id"],
                                                         self.user_data_info["createTime"])
                except Exception as e:
                    print(e)

            current_time = time.time()
            # 每10秒钟，请求一次锁的状态
            if current_time - start_time > 2:
                start_time = current_time
                try:
                    self.requestLockStatus(self.device, DEVICE_ID)
                except Exception as e:
                    print("请求锁的状态网络异常")
                    print(e)


if __name__ == "__main__":
    print("=============================================")
    print("**************  无人售货柜开始启动  *****************")
    print("=============================================")
    try:
        app = MachineApplication()
        app.startMachineBox()
        # app.requestCloseLock("f2195930723011e9b0a2525400c99203")
    except Exception as e:
        print("启动失败")
        print(e)



