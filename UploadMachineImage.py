#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !
import cv2
import time
import requests
import base64
import json
import os
import threading

camera_count = 4  # 相机的个数

# 绘制检测所花的时长
def draw_str(dst, target, s):
    x, y = target
    cv2.putText(dst, s, (x + 1, y + 1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)

def open_camera(camera_id):
    camera = cv2.VideoCapture(camera_id)
    camera.set(1, 20.0)  # FPS
    camera.set(3, 480)  # 宽
    camera.set(4, 320)  # 高
    return camera


# 上传图片
def upload_data(data):
    url = "http://118.24.93.53:5209"
    print("Request#url=%s" % url)

    try:

        req = requests.post(url=url, json=data)
        print("Response#%s" % req.text)
        if req.status_code == 200:
            print(req.text)
    except Exception as e:
        print("上传设备信息服务器异常")
        print(e)


# 创建根目录
def getFilePath(orderName):
    path = "./image/"
    if not os.path.exists(path):
        os.mkdir(path)

    path += str(orderName)
    if not os.path.exists(path):
        os.mkdir(path)

    return path

# 采集图像
def save_camera_image(device_id, wxOpenId, orderId, createTime):
    request_data = {"deviceId": device_id, "wxOpenId": wxOpenId, "orderId": orderId, "createTime": createTime}
    request_data["data"] = []

    # 创新订单目录
    order_dir = getFilePath(orderId)

    print("开始时间：", time.strftime("%Y-%m-%d_%H:%M:%S"))
    for i in range(0, camera_count):
        print("打开相机#%d" % i)

        # 打开相机
        camera = open_camera(i)
        # sleep(2)
        rect, frame = camera.read()

        for j in range(1, 25):
            rect, frame = camera.read()

        # 绘制相机编号
        draw_str(frame, (20, 20), 'camera#%d' % i)

        # 保存图片
        file_name = "{0}/{1}_{2}_.jpg"
        file_name = file_name.format(order_dir, "camera", i)

        cv2.imwrite(file_name, frame)
        print("camera#{0} save image# {1}".format(i, file_name))

        image_data = {}

        # 图片base64转码
        with open(file_name, "rb") as imageFile:
            encode_str = base64.b64encode(imageFile.read())
            image_data["image"] = str(encode_str, 'utf-8')

        # 相机编号
        image_data["camera_id"] = i
        request_data["data"].append(image_data)
        # 关闭相机
        camera.release()

    print("采集图像完成:", time.strftime("%Y-%m-%d %H:%M:%S"))
    thread = threading.Thread(name="upload", target=upload_data, args=(request_data,))
    thread.start()

    # upload_data(request_data)
    print("结束上传货柜信息时间：", time.strftime("%Y-%m-%d %H:%M:%S"))

# 上传设备状态
def upload_device_status(data):
    url = "https://vem.bailianic.com/front/wx/status/upload"
    print("Request#url=%s" % url)

    request_data = json.dumps(data["cameraJson"])
    data["cameraJson"] = request_data

    req = requests.post(url=url, data=data)

    print("Response#%s" % req.text)

    if req.status_code == 200:
        print(req.text)


def verify_image_empty(image):
    count = 0

    print(type(image), image.size, image.shape)

    row = int(image.shape[0]/2)
    col = int(image.shape[1]/2)
    for i in range(row, col):
        for j in range(row, col):
            # print("color# ", image[i, j], image[i, j][2])
            if image[i, j][2] < 128:
                count += 1

    print("---------------verify result#%d" % count)
    if count >= 20:
        return True
    else:
        return False


# 上传到微信的服务端 door_status#1:表示开门;2:表示关门
def upload_camera_image(device_id, door_status):
    request_data = {"deviceId": device_id, "status": door_status}
    request_data["cameraJson"] = []

    for i in range(0, camera_count):
        print("打开相机#%d" % i)

        # 打开相机
        camera = open_camera(i)
        # sleep(2)
        rect, frame = camera.read()
        #
        # # 检测摄像头是否初始化完毕，以10x10色块比较算法校验
        verify_is_empty = verify_image_empty(frame)
        while verify_is_empty:
            print("camera_id# %d" % i)
            rect, frame = camera.read()
            verify_is_empty = verify_image_empty(frame)

        # 绘制相机编号
        draw_str(frame, (20, 20), 'camera#%d' % i)

        # 保存图片
        file_name = "_%d_.jpg" % i
        # file_name = time.strftime("%Y-%m-%d %H:%M:%s") + "_%d_.jpg" % i
        cv2.imwrite(file_name, frame)
        print("camera#{0} save image# {1}".format(i, file_name))

        image_data = {}

        # 图片base64转码
        with open(file_name, "rb") as imageFile:
            encode_str = base64.b64encode(imageFile.read())
            image_data["image"] = str(encode_str, 'utf-8')

        # 相机编号
        image_data["cameraId"] = i

        request_data["cameraJson"].append(image_data)

        # 关闭相机
        camera.release()

    # upload_device_status(request_data)
    thread = threading.Thread(name="upload", target=upload_device_status, args=(request_data,))
    thread.start()


def test_open_camera():
    # camera = cv2.VideoCapture(1)
    camera = open_camera(3)
    while True:
        rect, frame = camera.read()
        cv2.imshow("Camera", frame)
        # 退出机制：点击键盘上面的字母 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            dir = getFilePath(974646)
            file_name = "{0}/{1}_{2}_.jpg"
            name = time.strftime("%H:%M:%S")
            print(type(name))
            file_name = file_name.format(dir, "camera", 1)
            print(file_name)
            cv2.imwrite(file_name, frame)
            break

if __name__ == "__main__":
    test_open_camera()
    # upload_camera_image("888", 1)
    # save_camera_image("888", "be3bc745c15f11e8a525246e9673b712", "be3bc745c15f11e8a525246e9673b712", 132323)

