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
from g_defs.c_tc358743 import TC358743
import hashlib
log = utils.log_utils.logging_init(__file__)

class Hdmi_In_Page(QObject):

    def __init__(self, mainwindow, **kwargs):
        super(Hdmi_In_Page, self).__init__(**kwargs)
        self.ffmpy_hdmi_in_cast_process = None
        self.mainwindow = mainwindow
        self.media_engine = mainwindow.media_engine
        self.preview_status = False
        self.b_hdmi_in_crop_enable = False

        self.hdmi_in_widget = QWidget(self.mainwindow.right_frame)
        self.hdmi_in_layout = QVBoxLayout()
        self.hdmi_in_widget.setLayout(self.hdmi_in_layout)

        self.mainwindow.right_layout.addWidget(self.hdmi_in_widget)

        self.preview_widget = QWidget(self.hdmi_in_widget)
        self.preview_widget_layout = QGridLayout()
        self.preview_widget.setLayout(self.preview_widget_layout)

        self.preview_label = QLabel(self.preview_widget)
        self.preview_label.setText("HDMI-in Preview")
        self.preview_label.setFixedHeight(320)
        self.preview_label.setScaledContents(True)

        self.play_action_btn = QPushButton(self.preview_widget)
        self.play_action_btn.setText("Start Play")
        self.play_action_btn.clicked.connect(self.send_to_led)
        self.preview_widget_layout.addWidget(self.preview_label, 0, 0)
        self.preview_widget_layout.addWidget(self.play_action_btn, 1, 0)

        # infomation of hdmi in
        self.info_widget = QWidget(self.hdmi_in_widget)
        self.info_widget_layout = QGridLayout()
        self.info_widget.setLayout(self.info_widget_layout)

        # width/height/fps
        self.hdmi_in_info_width_label = QLabel(self.info_widget)
        self.hdmi_in_info_width_label.setText("HDMI_In Width:")
        self.hdmi_in_info_width_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_width_res_label.setText("NA")

        self.hdmi_in_info_height_label = QLabel(self.info_widget)
        self.hdmi_in_info_height_label.setText("HDMI_In Height:")
        self.hdmi_in_info_height_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_height_res_label.setText("NA")

        self.hdmi_in_info_fps_label = QLabel(self.info_widget)
        self.hdmi_in_info_fps_label.setText("HDMI_In FPS:")
        self.hdmi_in_info_fps_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_fps_res_label.setText("NA")

        self.hdmi_in_crop_status_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_label.setText("Crop Disable")

        self.hdmi_in_crop_status_x_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_x_label.setText("Crop Start X:")
        self.hdmi_in_crop_status_x_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_x_res_label.setText("NA")

        self.hdmi_in_crop_status_y_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_y_label.setText("Crop Start Y:")
        self.hdmi_in_crop_status_y_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_y_res_label.setText("NA")

        self.hdmi_in_crop_status_w_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_w_label.setText("Crop Width:")
        self.hdmi_in_crop_status_w_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_w_res_label.setText("NA")

        self.hdmi_in_crop_status_h_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_h_label.setText("Crop Height:")
        self.hdmi_in_crop_status_h_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_h_res_label.setText("NA")


        self.info_widget_layout.addWidget(self.hdmi_in_info_width_label, 0, 0)
        self.info_widget_layout.addWidget(self.hdmi_in_info_width_res_label, 0, 1)
        self.info_widget_layout.addWidget(self.hdmi_in_info_height_label, 0, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_info_height_res_label, 0, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_info_fps_label, 0, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_info_fps_res_label, 0, 5)

        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_label, 1, 0)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_x_label, 2, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_x_res_label, 2, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_y_label, 2, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_y_res_label, 2, 5)

        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_w_label, 3, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_w_res_label, 3, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_h_label, 3, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_h_res_label, 3, 5)


        # crop setting of hdmi in
        self.crop_setting_widget = QWidget(self.hdmi_in_widget)
        self.crop_setting_widget_layout = QGridLayout()
        self.crop_setting_widget.setLayout(self.crop_setting_widget_layout)

        self.hdmi_in_crop_x_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_x_label.setText("Crop Start X:")
        self.hdmi_in_crop_x_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_x_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_x_lineedit.setText("NA")

        self.hdmi_in_crop_y_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_y_label.setText("Crop Start Y:")
        self.hdmi_in_crop_y_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_y_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_y_lineedit.setText("NA")

        self.hdmi_in_crop_w_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_w_label.setText("Crop Width:")
        self.hdmi_in_crop_w_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_w_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_w_lineedit.setText("NA")

        self.hdmi_in_crop_h_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_h_label.setText("Crop Height:")
        self.hdmi_in_crop_h_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_h_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_h_lineedit.setText("NA")

        self.hdmi_in_crop_disable_btn = QPushButton(self.crop_setting_widget)
        self.hdmi_in_crop_disable_btn.setFixedWidth(100)
        self.hdmi_in_crop_disable_btn.setText("Disable")
        self.hdmi_in_crop_disable_btn.clicked.connect(self.hdmi_in_crop_disable)

        self.hdmi_in_crop_enable_btn = QPushButton(self.crop_setting_widget)
        self.hdmi_in_crop_enable_btn.setFixedWidth(100)
        self.hdmi_in_crop_enable_btn.setText("Enable")
        self.hdmi_in_crop_enable_btn.clicked.connect(self.hdmi_in_crop_enable)

        self.hdmi_in_crop_dummy_label = QLabel(self.crop_setting_widget)

        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_x_label, 0, 0)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_x_lineedit, 0, 1)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_y_label, 0, 2)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_y_lineedit, 0, 3)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_dummy_label, 0, 4)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_disable_btn, 0, 5)

        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_w_label, 1, 0)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_w_lineedit, 1, 1)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_h_label, 1, 2)
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_h_lineedit, 1, 3)
        
        self.crop_setting_widget_layout.addWidget(self.hdmi_in_crop_enable_btn, 1, 5)

        # color setting of hdmi in
        self.setting_widget = QWidget(self.hdmi_in_widget)
        self.setting_widget_layout = QGridLayout()
        self.setting_widget.setLayout(self.setting_widget_layout)


        # brightness
        self.brightness_label = QLabel(self.setting_widget)
        self.brightness_label.setText("Brightness:")
        self.brightness_edit = QLineEdit(self.setting_widget)
        self.brightness_edit.setFixedWidth(100)
        self.brightness_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_brightness))

        # contrast
        self.contrast_label = QLabel(self.setting_widget)
        self.contrast_label.setText("Contrast:")
        self.contrast_edit = QLineEdit(self.setting_widget)
        self.contrast_edit.setFixedWidth(100)
        self.contrast_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_contrast))

        # red gain
        self.redgain_label = QLabel(self.setting_widget)
        self.redgain_label.setText("Red Gain:")
        self.redgain_edit = QLineEdit(self.setting_widget)
        self.redgain_edit.setFixedWidth(100)
        self.redgain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_red_bias))

        # green gain
        self.greengain_label = QLabel(self.setting_widget)
        self.greengain_label.setText("Green Gain:")
        self.greengain_edit = QLineEdit(self.setting_widget)
        self.greengain_edit.setFixedWidth(100)
        self.greengain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_green_bias))

        # blue gain
        self.blugain_label = QLabel(self.setting_widget)
        self.blugain_label.setText("Blue Gain:")
        self.bluegain_edit = QLineEdit(self.setting_widget)
        self.bluegain_edit.setFixedWidth(100)
        self.bluegain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_blue_bias))

        # client brightness adjust
        self.client_brightness_label = QLabel(self.setting_widget)
        self.client_brightness_label.setText("Client Br:")
        self.client_brightness_edit = QLineEdit(self.setting_widget)
        self.client_brightness_edit.setFixedWidth(100)
        self.client_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_brightness))

        # client brightness adjust
        self.client_br_divisor_label = QLabel(self.setting_widget)
        self.client_br_divisor_label.setText("Client BrDivisor:")
        self.client_br_divisor_edit = QLineEdit(self.setting_widget)
        self.client_br_divisor_edit.setFixedWidth(100)
        self.client_br_divisor_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_br_divisor))

        # client contrast(black level) adjust
        self.client_contrast_label = QLabel(self.setting_widget)
        self.client_contrast_label.setText("Client Black-Lv:")
        self.client_contrast_edit = QLineEdit(self.setting_widget)
        self.client_contrast_edit.setFixedWidth(100)
        self.client_contrast_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_contrast))

        # client gamma adjust
        self.client_gamma_label = QLabel(self.setting_widget)
        self.client_gamma_label.setText("Client Gamma:")
        self.client_gamma_edit = QLineEdit(self.setting_widget)
        self.client_gamma_edit.setFixedWidth(100)
        self.client_gamma_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_gamma))

        self.video_params_confirm_btn = QPushButton(self.setting_widget)
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
        self.hdmi_in_layout.addWidget(self.info_widget)
        self.hdmi_in_layout.addWidget(self.crop_setting_widget)
        self.hdmi_in_layout.addWidget(self.setting_widget)
        
        #self.hdmi_in_cast_type = "h264"
        self.hdmi_in_cast_type = "v4l2"

        #self.cv2camera = CV2Camera(cv2_preview_h264_sink, self.hdmi_in_cast_type)
        self.cv2camera = CV2Camera(cv2_preview_v4l2_sink, self.hdmi_in_cast_type)
        self.cv2camera.signal_get_rawdata.connect(self.getRaw)
        self.cv2camera.signal_cv2_read_fail.connect(self.cv2_read_or_open_fail)

        # self.ffmpy_hdmi_in_cast_pid = None

        self.tc358743 = TC358743()
        self.tc358743.signal_refresh_tc358743_param.connect(self.refresh_tc358743_param)
        self.tc358743.get_tc358743_dv_timing()
        self.media_engine.media_processor.signal_play_hdmi_in_start_ret.connect(
            self.play_hdmi_in_start_ret)
        self.media_engine.media_processor.signal_play_hdmi_in_finish_ret.connect(
            self.play_hdmi_in_finish_ret)

    def start_hdmi_in_preview(self):

        if self.ffmpy_hdmi_in_cast_process is None:
            if self.hdmi_in_cast_type == "v4l2":
                self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_v4l2()
            else:
                self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_h264()

        if self.ffmpy_hdmi_in_cast_process is not None:
            # self.ffmpy_hdmi_in_cast_pid = self.ffmpy_hdmi_in_cast_process.pid
            self.cv2camera.set_hdmi_in_cast(True)
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
        hdmi_in_cast_out = ["udp://127.0.0.1:10011"]

        ffmpy_hdmi_in_cast_process = self.media_engine.start_hdmi_in_h264("/dev/video0", hdmi_in_cast_out)
        if ffmpy_hdmi_in_cast_process is None:
            log.debug("ffmpy_hdmi_in_cast_process is None")
            self.preview_label.setText("Please Check HDMI-in Dongle")
        else:
            log.debug("ffmpy_hdmi_in_cast_process is alive")
            self.preview_label.setText("Please Wait for singal")
        return ffmpy_hdmi_in_cast_process

    def start_hdmi_in_cast_v4l2(self):
        hdmi_in_cast_out = ["/dev/video5", "/dev/video6"]

        ffmpy_hdmi_in_cast_process = self.media_engine.start_hdmi_in_v4l2("/dev/video0", hdmi_in_cast_out)
        if ffmpy_hdmi_in_cast_process is None:
            log.debug("ffmpy_hdmi_in_cast_process is None")
            self.preview_label.setText("Please Check HDMI-in Dongle")
        else:
            log.debug("ffmpy_hdmi_in_cast_process is alive")
            self.preview_label.setText("Please Wait for singal")

        return ffmpy_hdmi_in_cast_process

    def stop_hdmi_in_cast(self):
        if self.ffmpy_hdmi_in_cast_process is not None:
            os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
        self.ffmpy_hdmi_in_cast_process = None
        # self.ffmpy_hdmi_in_cast_pid = None

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

        if self.media_engine.media_processor.play_hdmi_in_worker is None:
            log.debug("Start streaming to led")
            video_src = "/dev/video6"
            streaming_sink = [udp_sink]
            self.media_engine.media_processor.hdmi_in_play(video_src, streaming_sink)
        else:
            log.debug("Stop streaming to led")
            self.media_engine.media_processor.play_hdmi_in_worker.stop()

    def play_hdmi_in_start_ret(self):
        log.debug("")
        self.play_action_btn.setText("STOP")

    def play_hdmi_in_finish_ret(self):
        log.debug("")
        self.play_action_btn.setText("START")

    def cv2_read_or_open_fail(self):
        # handle re-init tc358743
        # Stop cast ffmpy first
        log.debug("")
        if self.ffmpy_hdmi_in_cast_process is not None:
            self.media_engine.media_processor.play_hdmi_in_work.force_stop = True
            os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
            self.ffmpy_hdmi_in_cast_process = None


        if self.tc358743.get_tc358743_hdmi_connected_status() is False:
            # run a timer to check???
            log.debug("No HDMI connected")
            self.cv2camera.set_hdmi_in_cast(False)
        else:
            log.debug("HDMI connected")
            if self.tc358743.set_tc358743_dv_bt_timing() is True:
                self.tc358743.reinit_tc358743_dv_timing()
                self.start_hdmi_in_preview()
                if self.ffmpy_hdmi_in_cast_process is not None:
                    self.cv2camera.set_hdmi_in_cast(True)
                else:
                    log.debug("self.ffmpy_hdmi_in_cast_process is None")

    def refresh_tc358743_param(self, connected, width, height, fps):
        log.debug("connected = %d", connected)
        if connected is True:
            self.hdmi_in_info_width_res_label.setText(str(width))
            self.hdmi_in_info_height_res_label.setText(str(height))
            self.hdmi_in_info_fps_res_label.setText(str(fps))
            # hdmi in crop enable/disable
            log.debug("self.b_hdmi_in_crop_enable : %d", self.b_hdmi_in_crop_enable)
            if self.b_hdmi_in_crop_enable is False:
                log.debug("")
                self.hdmi_in_crop_status_x_res_label.setText("0")
                self.hdmi_in_crop_status_y_res_label.setText("0")
                self.hdmi_in_crop_status_w_res_label.setText(str(width))
                self.hdmi_in_crop_status_h_res_label.setText(str(height))
                self.hdmi_in_crop_x_lineedit.setText("0")
                self.hdmi_in_crop_y_lineedit.setText("0")
                self.hdmi_in_crop_w_lineedit.setText(str(width))
                self.hdmi_in_crop_h_lineedit.setText(str(height))

                
        else:
            self.hdmi_in_crop_status_x_res_label.setText("0")
            self.hdmi_in_crop_status_y_res_label.setText("0")
            self.hdmi_in_crop_status_w_res_label.setText(str(self.tc358743.hdmi_width))
            self.hdmi_in_crop_status_h_res_label.setText(str(self.tc358743.hdmi_height))
            self.hdmi_in_crop_x_lineedit.setText("0")
            self.hdmi_in_crop_y_lineedit.setText("0")
            self.hdmi_in_crop_w_lineedit.setText(str(self.tc358743.hdmi_width))
            self.hdmi_in_crop_h_lineedit.setText(str(self.tc358743.hdmi_width))

    def hdmi_in_crop_disable(self):
        self.b_hdmi_in_crop_enable = False
        self.video_crop_disable()

    def hdmi_in_crop_enable(self):
        log.debug("")
        self.b_hdmi_in_crop_enable = True
        self.video_crop_enable()

    def video_crop_enable(self):
        log.debug("crop_enable")
        self.hdmi_in_crop_status_label.setText("Crop Enable")
        self.hdmi_in_crop_status_x_res_label.setText(self.hdmi_in_crop_x_lineedit.text())
        self.hdmi_in_crop_status_y_res_label.setText(self.hdmi_in_crop_y_lineedit.text())
        self.hdmi_in_crop_status_w_res_label.setText(self.hdmi_in_crop_w_lineedit.text())
        self.hdmi_in_crop_status_h_res_label.setText(self.hdmi_in_crop_h_lineedit.text())
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            utils.ffmpy_utils.ffmpy_crop_enable(self.hdmi_in_crop_x_lineedit.text(),
                                         self.hdmi_in_crop_y_lineedit.text(),
                                         self.hdmi_in_crop_w_lineedit.text(),
                                         self.hdmi_in_crop_h_lineedit.text(),
                                         self.mainwindow.led_wall_width,
                                         self.mainwindow.led_wall_height)


    def video_crop_disable(self):
        log.debug("crop_disable")
        self.hdmi_in_crop_status_label.setText("Crop Disable")
        self.hdmi_in_crop_status_x_res_label.setText("0")
        self.hdmi_in_crop_status_y_res_label.setText("0")
        self.hdmi_in_crop_status_w_res_label.setText(str(self.tc358743.hdmi_width))
        self.hdmi_in_crop_status_h_res_label.setText(str(self.tc358743.hdmi_height))
        self.hdmi_in_crop_x_lineedit.setText("0")
        self.hdmi_in_crop_y_lineedit.setText("0")
        self.hdmi_in_crop_w_lineedit.setText(str(self.tc358743.hdmi_width))
        self.hdmi_in_crop_h_lineedit.setText(str(self.tc358743.hdmi_height))
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            utils.ffmpy_utils.ffmpy_crop_disable(self.mainwindow.led_wall_width,
                                     self.mainwindow.led_wall_height)