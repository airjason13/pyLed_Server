import cv2
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class CV2Camera(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    signal_get_rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    signal_cv2_read_fail = QtCore.pyqtSignal()

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
        self.preview_frame_count = 0
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.fps_counter)
        self.fps = 0
        self.fps_timer.start(1000)
        # 建立 cv2 的攝影機物件

        self.hdmi_in_cast = False
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
                log.debug("A")
                if not self.connect:
                    log.debug("B")
                    self.cam = self.open_tc358743_cam()
                    if self.cam is None:
                        log.debug("C")
                        self.signal_cv2_read_fail.emit()
                        time.sleep(2)
                        continue

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
                self.preview_frame_count += 1
                if self.preview_frame_count % 5 == 0:
                    #img = cv2.resize(img, (160, 120))
                    self.signal_get_rawdata.emit(img)    # 發送影像
            else:    # 例外處理
                log.debug("No frame read!!!")
                self.connect = False

                self.hdmi_in_cast = False
                self.cam.release()
                self.cam = None
                self.signal_cv2_read_fail.emit()
            time.sleep(0.1)
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

    def fps_counter(self):
        self.fps = self.preview_frame_count
        self.preview_frame_count = 0

    def open_tc358743_cam(self):
        cam = None
        if self.hdmi_in_cast is True:
            cam = cv2.VideoCapture(self.video_src)
        return cam

    def set_hdmi_in_cast(self, b_value):
        self.hdmi_in_cast = b_value
