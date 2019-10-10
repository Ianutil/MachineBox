#!/usr/bin/python
# -*- coding: UTF-8 
# author: Ian
# Please,you must believe yourself who can do it beautifully !

import pygame
import time
import mp3play
# import win32api
import os

# url = "http://jsdx.sc.chinaz.com/Files/DownLoad/sound1/201503/5581.wav"
OPEN_DOOR_SOUND = "./source/Baidu-TTS.mp3"
CLOSE_DOOR_SOUND = "./source/Baidu-TTS-2.mp3"

pygame.mixer.init()

track = pygame.mixer.music.load(OPEN_DOOR_SOUND)
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play()
time.sleep(10)
pygame.mixer.music.stop()


# 貌似只能播放单声道音乐，可能是pygame模块限制
def playMusic(filename, loops=0, start=0.0, value=0.5):
    """
    :param filename: 文件名
    :param loops: 循环次数
    :param start: 从多少秒开始播放
    :param value: 设置播放的音量，音量value的范围为0.0到1.0
    :return:
    """
    flag = False  # 是否播放过
    pygame.mixer.init()  # 音乐模块初始化

    screen = pygame.display.set_mode((640, 480), 0, 32)
    # 创建了一个窗口
    pygame.display.set_caption("Hello, World!")
    # 设置窗口标题

    while 1:
        if flag == 0:
            pygame.mixer.music.load(filename)
            # pygame.mixer.music.play(loops=0, start=0.0) loops和start分别代表重复的次数和开始播放的位置。
            pygame.mixer.music.play(loops=loops, start=start)
            pygame.mixer.music.set_volume(value)  # 来设置播放的音量，音量value的范围为0.0到1.0。
        if pygame.mixer.music.get_busy() == True:
            flag = True
        else:
            if flag:
                pygame.mixer.music.stop()  # 停止播放
                break


def playMp3(file):

    media = mp3play.load(file)
    media.play()
    # duration= media.milliseconds()
    # time.sleep(duration)
    time.sleep(10)
    media.stop()

def playMp3ForWin32(file):
    # ShellExecute 查找与指定文件关联在一起的程序的文件名
    # 第一个参数默认为0,打开，路径名，默认空，默认空，是否显示程序1or0
    # win32api.ShellExecute(0, 'open', OPEN_DOOR_SOUND, '', '', 1)

    os.system(OPEN_DOOR_SOUND)
    # os.system("sudo " + OPEN_DOOR_SOUND)

if "__main__" == __name__ :
    playMusic(OPEN_DOOR_SOUND, 0, 0, 1.0)
    playMp3(OPEN_DOOR_SOUND)
    playMp3ForWin32(OPEN_DOOR_SOUND)

    print("Hello World")