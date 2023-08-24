import cv2
import numpy as np
import time
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QMutex
import utils.log_utils
import ctypes
from global_def import *
import utils.file_utils



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
        try:
            self.fps_timer.start(1000)
        except Exception as e:
            log.debug(e)
        # 建立 cv2 的攝影機物件

        # self.hdmi_in_cast = False
        # self.connect = False
        # self.running = False
        self.force_quit = False
        self.cam = None
        self.cam_mutex = QMutex()
        self.release_cam = False

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        os.environ['OPENCV_VIDEO_PRIORITY_MSMF'] = '0'
        os.environ['OPENCV_V4L2_CAPTURE_OPTION'] = 'timeout:10'
        log.debug("start to run")
        log.debug("self.video_src = %s", self.video_src)
        try:
            self.cam = cv2.VideoCapture(self.video_src, cv2.CAP_V4L2)
        except Exception as e:
            log.fatal(e)

        # 當正常連接攝影機才能進入迴圈
        # while self.running and self.connect:
        # while True:

        no_frame_read_count = 0
        while True:
            self.cam_mutex.lock()
            ret = False
            try:
                if self.cam is None:
                    log.debug("self.cam is None")
                    self.cam_mutex.unlock()
                    break
                ret, img = self.cam.read()    # 讀取影像
                
                if self.release_cam is True:
                    log.debug("cv2 release cam")
                    self.cam.release()
                    for i in range(50):
                        if self.cam.isOpened() is False:
                            break
                        log.debug("cam is still open %d", i)
                    self.cam = None
                    self.cam_mutex.unlock()
                    break

                if ret:
                    no_frame_read_count = 0
                    self.preview_frame_count += 1
                    if self.preview_frame_count % 10 == 0:
                        # img = cv2.resize(img, (320, 240))
                        self.signal_get_rawdata.emit(img)    # 發送影像
                        self.preview_frame_count = 0
                else:    # 例外處理
                    # log.debug("No frame read @%s", self.video_src)
                    no_frame_read_count += 1
                    if no_frame_read_count > 5:
                        log.debug("No frame read @%s", self.video_src)
                        # utils.file_utils.find_ffmpeg_process()
                        # test release cam
                        # self.release_cam = True


                    # self.connect = False
                    # self.hdmi_in_cast = False
                    '''self.cam.release()
                    for i in range(50):
                        if self.cam.isOpened() is False:
                            break
                        log.debug("cam is still open %d", i)
                    self.cam = None'''
                    # self.signal_cv2_read_fail.emit()
            except Exception as e:
                log.debug(e)
            finally: 
                self.cam_mutex.unlock()
            time.sleep(0.1)
        log.debug("stop to run")
        self.cam_mutex.lock()
        if self.cam is not None:
            try:
                self.cam.release()
            except Exception as e:
                log.fatal(e)

            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)
            self.cam = None
        self.cam_mutex.unlock()
        self.quit()


    '''def open(self):
        """ 開啟攝影機影像讀取功能 """
        # if self.connect:
        #    self.running = True    # 啟動讀取狀態'''

    '''def stop(self):
        """ 暫停攝影機影像讀取功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態'''

    def close(self):
        """ 關閉攝影機功能 """
        self.cam_mutex.lock()
        self.release_cam = True
        '''if self.cam is not None:
            self.cam.release()      # 釋放攝影機

            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)

            self.cam = None'''
        self.cam_mutex.unlock()
        # self.force_quit = True

    def fps_counter(self):
        self.fps = self.preview_frame_count
        self.preview_frame_count = 0

    def open_tc358743_cam(self):
        self.cam_mutex.lock()
        if self.cam is not None:
            self.cam.release()
            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)
            self.cam = None
            self.cam = cv2.VideoCapture(self.video_src)
        self.cam_mutex.unlock()

    def close_tc358743_cam(self):
        self.cam_mutex.lock()
        self.release_cam = True

        """if self.cam is not None:
            self.cam.release()
            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)
            self.cam = None"""
        self.cam_mutex.unlock()

    def set_hdmi_in_cast(self, b_value):
        log.debug("depreciated")

        # self.hdmi_in_cast = b_value
