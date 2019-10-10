#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !
import MachineApplication
import os



if __name__ == "__main__":
    print("=============================================")
    print("**************  无人售货柜开始启动  *****************")
    print("=============================================")
    try:
        app = MachineApplication.MachineApplication()
        app.startMachineBox()
    except Exception as e:
        print("启动失败")
        print(e)
        os.system("python.exe D:/Workspace/MachineBox/MachineBox.py")


