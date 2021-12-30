import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QImage
from PyQt5.QtWidgets import QTreeWidget, QTableWidget, QWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, \
                            QTreeWidgetItem, QPushButton, QHBoxLayout, QMenu, QAction
from g_defs.c_TreeWidgetItemSP import CTreeWidget
import os
from global_def import *
from set_qstyle import *
from c_new_playlist_dialog import NewPlaylistDialog
from commands_def import *
import utils.log_utils
import utils.ffmpy_utils
from g_defs.c_cv2_camera import CV2Camera
import signal
import hashlib
log = utils.log_utils.logging_init(__file__)

class Hdmi_In_Page(QObject):

    def __init__(self, mainwindow, **kwargs):
        super(Hdmi_In_Page, self).__init__(**kwargs)
        self.mainwindow = mainwindow

        self.hdmi_in_widget = QWidget(self.mainwindow.right_frame)
        self.hdmi_in_layout = QVBoxLayout()
        self.hdmi_in_widget.setLayout(self.hdmi_in_layout)

        self.mainwindow.right_layout.addWidget(self.hdmi_in_widget)

        self.preview_widget = QWidget(self.hdmi_in_widget)
        self.preview_widget_layout = QGridLayout()
        self.preview_widget.setLayout(self.preview_widget_layout)

        self.preview_label = QLabel(self.preview_widget)
        self.preview_label.setText("HDMI-in Preview")
        self.preview_widget_layout.addWidget(self.preview_label, 0, 0)

        self.setting_widget = QWidget(self.hdmi_in_widget)
        self.setting_widget_layout = QGridLayout()
        self.setting_widget.setLayout(self.setting_widget_layout)

        self.test_btn = QPushButton(self.setting_widget)
        self.test_btn.setText("TEST")
        self.setting_widget_layout.addWidget(self.test_btn, 0, 0)

        self.hdmi_in_layout.addWidget(self.preview_widget)
        self.hdmi_in_layout.addWidget(self.setting_widget)

        self.cv2camera = CV2Camera()
        self.cv2camera.signal_get_rawdata.connect(self.getRaw)

        self.ffmpy_hdmi_in_cast_pid = None

    def start_hdmi_in_preview(self):

        if self.ffmpy_hdmi_in_cast_pid is None:
            self.start_hdmi_in_cast()
        log.debug("self.ffmpy_hdmi_in_cast_process.pid : %d", self.ffmpy_hdmi_in_cast_process.pid)
        self.cv2camera.open()  # 影像讀取功能開啟
        self.cv2camera.start()  # 在子緒啟動影像讀取

    def stop_hdmi_in_preview(self):
        log.debug("")
        self.cv2camera.stop()  # 關閉
        self.stop_hdmi_in_cast()

    def getRaw(self, data):  # data 為接收到的影像
        """ 取得影像 """
        self.showData(data)  # 將影像傳入至 showData()

    def showData(self, img):
        """ 顯示攝影機的影像 """
        self.Ny, self.Nx, _ = img.shape  # 取得影像尺寸

        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)

        # 建立 Qimage 物件 (RGB格式)
        qimg = QImage(img.data, self.Nx, self.Ny, QImage.Format_BGR888)

        # viewData 的顯示設定
        self.preview_label.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 viewData 上
        self.preview_label.setPixmap(QPixmap.fromImage(qimg))

    def start_hdmi_in_cast(self):
        hdmi_in_cast_out = []
        hdmi_in_cast_out.append("/dev/video5")
        hdmi_in_cast_out.append("/dev/video6")

        self.ffmpy_hdmi_in_cast_process = utils.ffmpy_utils.neo_ffmpy_cast_video("/dev/video0", hdmi_in_cast_out, 160, 108)

    def stop_hdmi_in_cast(self):
        os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
        self.ffmpy_hdmi_in_cast_process = None