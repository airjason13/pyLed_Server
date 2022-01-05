import cv2
import numpy as np
import time
from PyQt5 import QtCore

import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class CV2Camera(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    signal_get_rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray

    def __init__(self, video_src, video_type, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
            - 建立 cv2 的 VideoCapture 物件
            - 設定屬性來確認狀態
              - self.connect：連接狀態
              - self.running：讀取狀態
        """
        # 將父類初始化
        super().__init__(parent)
        self.video_src = video_src
        self.video_type = video_type
        # 建立 cv2 的攝影機物件
        if self.video_type == "v4l2":
            self.cam = cv2.VideoCapture(self.video_src)
            # 判斷攝影機是否正常連接
            if self.cam is None or not self.cam.isOpened():
                self.connect = False
                self.running = False
            else:
                self.connect = True
                self.running = False
        else:
            self.connect = False
            self.running = False
            self.cam = None

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        log.debug("start to run")
        log.debug("self.video_src = %s", self.video_src)
        # 當正常連接攝影機才能進入迴圈
        # while self.running and self.connect:
        while True:
            if self.cam is None or not self.cam.isOpened():
                if self.connect == False:
                    if self.video_type == "h264":
                        self.cam = cv2.VideoCapture(self.video_src)
                    else:
                        self.cam = cv2.VideoCapture(self.video_src)
                time.sleep(1)

                if self.cam is None or not self.cam.isOpened():
                    self.connect = False
                    self.running = False
                else:
                    self.connect = True
                    self.running = True

            if self.running is False:
                log.debug("waiting for start to read")
                time.sleep(1)
                continue

            ret, img = self.cam.read()    # 讀取影像
            if ret:
                img = cv2.resize(img, (640, 480))
                self.signal_get_rawdata.emit(img)    # 發送影像
            else:    # 例外處理
                log.debug("Warning!!!")
                self.connect = False
        log.debug("stop to run")

    def open(self):
        """ 開啟攝影機影像讀取功能 """
        if self.connect:
            self.running = True    # 啟動讀取狀態

    def stop(self):
        """ 暫停攝影機影像讀取功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態

    def close(self):
        """ 關閉攝影機功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態
            time.sleep(1)
            self.cam.release()      # 釋放攝影機