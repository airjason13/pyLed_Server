import cv2
import numpy as np
import time
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QMutex
import utils.log_utils
from PyQt5.QtWidgets import QApplication, QMainWindow

from qlocalmessage import send_preview_frame

log = utils.log_utils.logging_init(__file__)

class CV2Camera(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    signal_get_rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    signal_cv2_read_fail = QtCore.pyqtSignal()

    # def __init__(self, video_src, video_type, parent=None):
    def __init__(self, video_src, preview_server, preview_fps, show_window):

        # 將父類初始化
        super().__init__()
        self.video_src = video_src
        self.preview_server = preview_server
        self.preview_frame_count = 0
        self.show_window = show_window
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.fps_counter)
        self.fps = 0
        self.fps_timer.start(1000)

        self.force_quit = False
        self.cam = None
        self.cam_mutex = QMutex()

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        log.debug("start to run")
        log.debug("self.video_src = %s", self.video_src)
        self.cam = cv2.VideoCapture(self.video_src)
        log.debug("self.cam : %s", self.cam)
        while True:
            self.cam_mutex.lock()
            try:
                if self.cam is None:
                    log.debug("self.cam is None")
                    self.cam_mutex.unlock()
                    break
                if self.force_quit is True:
                    log.debug("self.force_quit")
                    self.cam_mutex.unlock()
                    break
                ret, img = self.cam.read()    # 讀取影像
                if ret:
                    self.preview_frame_count += 1
                    if self.preview_frame_count % 5 == 0:
                        send_preview_frame(img)    # 發送影像
                        log.debug("send preview frame")
                        '''if self.show_window is True:
                            cv2.imshow("preview", img)
                            self.preview_frame_count = 0'''

                else:    # 例外處理
                    log.debug("No frame read!!!")

                    self.cam.release()
                    for i in range(50):
                        if self.cam.isOpened() is False:
                            break
                        log.debug("cam is still open %d", i)
                    self.cam = None

            except Exception as e:
                log.debug(e)
            finally:
                self.cam_mutex.unlock()
            time.sleep(0.1)
        log.debug("stop to run")
        self.cam_mutex.lock()
        if self.cam is not None:
            self.cam.release()
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
        if self.cam is not None:
            self.cam.release()      # 釋放攝影機

            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)

            self.cam = None
        self.cam_mutex.unlock()
        self.force_quit = True

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
        if self.cam is not None:
            self.cam.release()
            for i in range(50):
                if self.cam.isOpened() is False:
                    break
                log.debug("cam is still open %d", i)
            self.cam = None
        self.cam_mutex.unlock()

    def set_hdmi_in_cast(self, b_value):
        log.debug("depreciated")

        # self.hdmi_in_cast = b_value


class MainUi(QMainWindow):
    def __init__(self, video_src, preview_server, preview_fps, show_window):
        super().__init__()
        self.setFixedSize(0, 0)
        self.cam = CV2Camera(video_src, preview_server, preview_fps, show_window=True)
        self.cam.start()

def main(argv):
    if len(argv) != 5:
        log.debug("cv2 camera argv error!")
        return

    video_src = argv[1]
    preview_server = argv[2]
    i_preview_fps = int(argv[3])
    i_show_window = int(argv[4])
    log.debug("video_src = %s", video_src)
    log.debug("preview_server = %s", preview_server)
    log.debug("preview_fps = %d", i_preview_fps)
    log.debug("preview_fps = %s", i_show_window)

    qt_app = QApplication(argv)
    gui = MainUi(video_src, preview_server, i_preview_fps, True)
    gui.show()
    #cam = CV2Camera(video_src, preview_server, i_preview_fps, show_window=True)

    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main(sys.argv)
