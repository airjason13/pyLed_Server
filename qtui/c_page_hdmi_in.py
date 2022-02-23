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
        self.media_engine = mainwindow.media_engine
        self.preview_status = False

        self.hdmi_in_widget = QWidget(self.mainwindow.right_frame)
        self.hdmi_in_layout = QVBoxLayout()
        self.hdmi_in_widget.setLayout(self.hdmi_in_layout)

        self.mainwindow.right_layout.addWidget(self.hdmi_in_widget)

        self.preview_widget = QWidget(self.hdmi_in_widget)
        self.preview_widget_layout = QGridLayout()
        self.preview_widget.setLayout(self.preview_widget_layout)

        self.preview_label = QLabel(self.preview_widget)
        self.preview_label.setText("HDMI-in Preview")

        self.play_action_btn = QPushButton(self.preview_widget)
        self.play_action_btn.setText("Start Play")
        self.play_action_btn.clicked.connect(self.send_to_led)
        self.preview_widget_layout.addWidget(self.preview_label, 0, 0)
        self.preview_widget_layout.addWidget(self.play_action_btn, 1, 0)


        self.setting_widget = QWidget(self.hdmi_in_widget)
        self.setting_widget_layout = QGridLayout()
        self.setting_widget.setLayout(self.setting_widget_layout)

        # self.test_btn = QPushButton(self.setting_widget)
        # self.test_btn.setText("TEST")

        # brightness
        self.brightness_label = QLabel(self.mainwindow.right_frame)
        self.brightness_label.setText("Brightness:")
        self.brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.brightness_edit.setFixedWidth(100)
        self.brightness_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_brightness))

        # contrast
        self.contrast_label = QLabel(self.mainwindow.right_frame)
        self.contrast_label.setText("Contrast:")
        self.contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.contrast_edit.setFixedWidth(100)
        self.contrast_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_contrast))

        # red gain
        self.redgain_label = QLabel(self.mainwindow.right_frame)
        self.redgain_label.setText("Red Gain:")
        self.redgain_edit = QLineEdit(self.mainwindow.right_frame)
        self.redgain_edit.setFixedWidth(100)
        self.redgain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_red_bias))

        # green gain
        self.greengain_label = QLabel(self.mainwindow.right_frame)
        self.greengain_label.setText("Green Gain:")
        self.greengain_edit = QLineEdit(self.mainwindow.right_frame)
        self.greengain_edit.setFixedWidth(100)
        self.greengain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_green_bias))

        # blue gain
        self.blugain_label = QLabel(self.mainwindow.right_frame)
        self.blugain_label.setText("Blue Gain:")
        self.bluegain_edit = QLineEdit(self.mainwindow.right_frame)
        self.bluegain_edit.setFixedWidth(100)
        self.bluegain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_blue_bias))

        # client brightness adjust
        self.client_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_brightness_label.setText("Client Br:")
        self.client_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_brightness_edit.setFixedWidth(100)
        self.client_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_brightness))

        # client brightness adjust
        self.client_br_divisor_label = QLabel(self.mainwindow.right_frame)
        self.client_br_divisor_label.setText("Client BrDivisor:")
        self.client_br_divisor_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_br_divisor_edit.setFixedWidth(100)
        self.client_br_divisor_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_br_divisor))

        # client contrast(black level) adjust
        self.client_contrast_label = QLabel(self.mainwindow.right_frame)
        self.client_contrast_label.setText("Client Black-Lv:")
        self.client_contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_contrast_edit.setFixedWidth(100)
        self.client_contrast_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_contrast))

        # client gamma adjust
        self.client_gamma_label = QLabel(self.mainwindow.right_frame)
        self.client_gamma_label.setText("Client Gamma:")
        self.client_gamma_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_gamma_edit.setFixedWidth(100)
        self.client_gamma_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_gamma))



        self.video_params_confirm_btn = QPushButton(self.mainwindow.right_frame)
        self.video_params_confirm_btn.setText("Set")
        self.video_params_confirm_btn.setFixedWidth(100)
        self.video_params_confirm_btn.clicked.connect(self.video_params_confirm_btn_clicked)

        #self.setting_widget_layout.addWidget(self.test_btn, 0, 0)
        self.setting_widget_layout.addWidget(self.redgain_label, 0, 0)
        self.setting_widget_layout.addWidget(self.redgain_edit, 0, 1)
        self.setting_widget_layout.addWidget(self.greengain_label, 0, 2)
        self.setting_widget_layout.addWidget(self.greengain_edit, 0, 3)
        self.setting_widget_layout.addWidget(self.blugain_label, 0, 4)
        self.setting_widget_layout.addWidget(self.bluegain_edit, 0, 5)

        self.setting_widget_layout.addWidget(self.brightness_label, 1, 0)
        self.setting_widget_layout.addWidget(self.brightness_edit, 1, 1)
        self.setting_widget_layout.addWidget(self.contrast_label, 1, 2)
        self.setting_widget_layout.addWidget(self.contrast_edit, 1, 3)

        self.setting_widget_layout.addWidget(self.client_brightness_label, 2, 0)
        self.setting_widget_layout.addWidget(self.client_brightness_edit, 2, 1)
        self.setting_widget_layout.addWidget(self.client_br_divisor_label, 2, 2)
        self.setting_widget_layout.addWidget(self.client_br_divisor_edit, 2, 3)
        self.setting_widget_layout.addWidget(self.client_contrast_label, 3, 0)
        self.setting_widget_layout.addWidget(self.client_contrast_edit, 3, 1)
        self.setting_widget_layout.addWidget(self.client_gamma_label, 4, 0)
        self.setting_widget_layout.addWidget(self.client_gamma_edit, 4, 1)
        self.setting_widget_layout.addWidget(self.video_params_confirm_btn, 4, 5)

        self.hdmi_in_layout.addWidget(self.preview_widget)
        self.hdmi_in_layout.addWidget(self.setting_widget)
        
        #self.hdmi_in_cast_type = "h264"
        self.hdmi_in_cast_type = "v4l2"

        #self.cv2camera = CV2Camera(cv2_preview_h264_sink, self.hdmi_in_cast_type)
        self.cv2camera = CV2Camera(cv2_preview_v4l2_sink, self.hdmi_in_cast_type)
        self.cv2camera.signal_get_rawdata.connect(self.getRaw)

        self.ffmpy_hdmi_in_cast_pid = None
        # self.hdmi_in_cast_type = "h264"
        # self.hdmi_in_cast_type = "v4l2"

        self.media_engine.media_processor.signal_play_hdmi_in_start_ret.connect(
            self.play_hdmi_in_start_ret)
        self.media_engine.media_processor.signal_play_hdmi_in_finish_ret.connect(
            self.play_hdmi_in_finish_ret)

    def start_hdmi_in_preview(self):
        if self.ffmpy_hdmi_in_cast_pid is None:
            if self.hdmi_in_cast_type == "v4l2":
                self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_v4l2()
            else:
                self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_h264()

        if self.ffmpy_hdmi_in_cast_process is not None:
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

        # 建立 Qimage 物件 (RGB格式)
        qimg = QImage(img.data, self.Nx, self.Ny, QImage.Format_BGR888)

        # viewData 的顯示設定
        self.preview_label.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 viewData 上
        self.preview_label.setPixmap(QPixmap.fromImage(qimg))

    def start_hdmi_in_cast_h264(self):
        hdmi_in_cast_out = []
        hdmi_in_cast_out.append("udp://127.0.0.1:10011")
        #hdmi_in_cast_out.append("udp://127.0.0.1:10012")

        ffmpy_hdmi_in_cast_process = self.media_engine.start_hdmi_in_h264("/dev/video0", hdmi_in_cast_out)
        if ffmpy_hdmi_in_cast_process is None:
            log.debug("ffmpy_hdmi_in_cast_process is None")
            self.preview_label.setText("Please Check HDMI-in Dongle")
        else:
            log.debug("ffmpy_hdmi_in_cast_process is alive")
            self.preview_label.setText("Please Wait for singal")
        return ffmpy_hdmi_in_cast_process

    def start_hdmi_in_cast_v4l2(self):
        hdmi_in_cast_out = []
        hdmi_in_cast_out.append("/dev/video5")
        # hdmi_in_cast_out.append("/dev/video6")

        ffmpy_hdmi_in_cast_process = self.media_engine.start_hdmi_in_v4l2("/dev/video0", hdmi_in_cast_out)
        if ffmpy_hdmi_in_cast_process is None:
            log.debug("ffmpy_hdmi_in_cast_process is None")
            self.preview_label.setText("Please Check HDMI-in Dongle")
        else:
            log.debug("ffmpy_hdmi_in_cast_process is alive")
            self.preview_label.setText("Please Wait for singal")
        return ffmpy_hdmi_in_cast_process

    def stop_hdmi_in_cast(self):
        if self.ffmpy_hdmi_in_cast_pid is not None:
            os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
        self.ffmpy_hdmi_in_cast_process = None

    def video_params_confirm_btn_clicked(self):
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
        if video_params.video_brightness != int(self.brightness_edit.text()):
            log.debug("brightness changed!")
            media_processor.set_brightness_level(int(self.brightness_edit.text()))
        if video_params.video_contrast != int(self.contrast_edit.text()):
            log.debug("contrast changed!")
            media_processor.set_contrast_level(int(self.contrast_edit.text()))
        if video_params.video_red_bias != int(self.redgain_edit.text()):
            log.debug("red gain changed!")
            media_processor.set_red_bias_level(int(self.redgain_edit.text()))
        if video_params.video_green_bias != int(self.greengain_edit.text()):
            log.debug("green gain changed!")
            media_processor.set_green_bias_level(int(self.greengain_edit.text()))
        if video_params.video_blue_bias != int(self.bluegain_edit.text()):
            log.debug("blue gain changed!")
            media_processor.set_blue_bias_level(int(self.bluegain_edit.text()))

    def send_to_led(self):
        log.debug("")
        video_src = "/dev/video6"
        streaming_sink = []
        streaming_sink.append(udp_sink)
        self.media_engine.media_processor.hdmi_in_play(video_src, streaming_sink)

    def play_hdmi_in_start_ret(self):
        log.debug("")
        self.play_action_btn.setText("STOP")

    def play_hdmi_in_finish_ret(self):
        log.debug("")
        self.play_action_btn.setText("START")