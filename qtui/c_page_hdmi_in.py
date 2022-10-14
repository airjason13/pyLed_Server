import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt, QThread, QMutex, QTimer
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QImage
from PyQt5.QtWidgets import QTreeWidget, QTableWidget, QWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, \
                            QTreeWidgetItem, QPushButton, QHBoxLayout, QMenu, QAction, QRadioButton,\
                            QGroupBox, QComboBox
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
from str_define import *
from subprocess import PIPE, Popen
import hashlib
from astral_hashmap import *
log = utils.log_utils.logging_init(__file__)


class Hdmi_In_Page(QObject):
    def __init__(self, mainwindow, **kwargs):
        super(Hdmi_In_Page, self).__init__(**kwargs)
        # the process of ffmpeg to cast to v4l2loopback device for preview
        self.ffmpy_hdmi_in_cast_process = None
        self.mainwindow = mainwindow
        self.media_engine = mainwindow.media_engine
        self.preview_status = False
        self.b_hdmi_in_crop_enable = False

        Popen("v4l2-ctl -d /dev/video3 -c timeout=600", shell=True, stdout=PIPE)
        Popen("v4l2-ctl -d /dev/video4 -c timeout=600", shell=True, stdout=PIPE)
        Popen("v4l2-ctl -d /dev/video5 -c timeout=600", shell=True, stdout=PIPE)

        self.hdmi_in_widget = QWidget(self.mainwindow.right_frame)
        self.hdmi_in_layout = QVBoxLayout()
        self.hdmi_in_widget.setLayout(self.hdmi_in_layout)

        self.mainwindow.right_layout.addWidget(self.hdmi_in_widget)
        log.debug("self.hdmi_in_widget.height() = %d", self.hdmi_in_widget.height())
        self.preview_widget = QWidget(self.hdmi_in_widget)

        self.preview_widget_layout = QGridLayout()
        self.preview_widget.setLayout(self.preview_widget_layout)

        self.preview_label = QLabel(self.preview_widget)
        self.preview_label.setText("HDMI-in Preview")
        self.preview_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.preview_label.setFixedHeight(320)
        self.preview_label.setScaledContents(True)

        self.play_action_btn = QPushButton(self.preview_widget)
        self.play_action_btn.setText("Start Play")
        self.play_action_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.play_action_btn.clicked.connect(self.send_to_led_parser)
        self.stop_action_btn = QPushButton(self.preview_widget)
        self.stop_action_btn.setText("Stop Play")
        self.stop_action_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.stop_action_btn.clicked.connect(self.stop_send_to_led)
        self.hdmi_in_play_status_label = QLabel(self.preview_widget)
        self.hdmi_in_play_status_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_play_status_label.setText("Non-Streaming")
        self.cast_pid_label = QLabel(self.preview_widget)
        self.cast_pid_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.cast_pid_label.setText("ff cast pid:None")
        self.ffmpy_pid_label = QLabel(self.preview_widget)
        self.ffmpy_pid_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.ffmpy_pid_label.setText("ffmpy pid:None")

        self.preview_widget_layout.addWidget(self.preview_label, 0, 0, 1, 2)
        self.preview_widget_layout.addWidget(self.play_action_btn, 2, 0)
        self.preview_widget_layout.addWidget(self.stop_action_btn, 2, 1)
        self.preview_widget_layout.addWidget(self.cast_pid_label, 3, 1)
        self.preview_widget_layout.addWidget(self.hdmi_in_play_status_label, 4, 0)
        self.preview_widget_layout.addWidget(self.ffmpy_pid_label, 4, 1)

        # infomation of hdmi in
        self.info_widget = QWidget(self.hdmi_in_widget)
        self.info_widget_layout = QGridLayout()
        self.info_widget.setLayout(self.info_widget_layout)

        # width/height/fps
        self.hdmi_in_info_width_label = QLabel(self.info_widget)
        self.hdmi_in_info_width_label.setText("HDMI_In Width:")
        self.hdmi_in_info_width_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_info_width_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_width_res_label.setText("NA")
        self.hdmi_in_info_width_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_info_height_label = QLabel(self.info_widget)
        self.hdmi_in_info_height_label.setText("HDMI_In Height:")
        self.hdmi_in_info_height_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_info_height_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_height_res_label.setText("NA")
        self.hdmi_in_info_height_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_info_fps_label = QLabel(self.info_widget)
        self.hdmi_in_info_fps_label.setText("HDMI_In FPS:")
        self.hdmi_in_info_fps_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_info_fps_res_label = QLabel(self.info_widget)
        self.hdmi_in_info_fps_res_label.setText("NA")
        self.hdmi_in_info_fps_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_status_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_label.setText("Crop Disable")
        self.hdmi_in_crop_status_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_status_x_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_x_label.setText("Crop Start X:")
        self.hdmi_in_crop_status_x_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_status_x_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_x_res_label.setText("NA")
        self.hdmi_in_crop_status_x_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_status_y_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_y_label.setText("Crop Start Y:")
        self.hdmi_in_crop_status_y_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_status_y_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_y_res_label.setText("NA")
        self.hdmi_in_crop_status_y_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_status_w_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_w_label.setText("Crop Width:")
        self.hdmi_in_crop_status_w_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_status_w_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_w_res_label.setText("NA")
        self.hdmi_in_crop_status_w_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_status_h_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_h_label.setText("Crop Height:")
        self.hdmi_in_crop_status_h_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_status_h_res_label = QLabel(self.info_widget)
        self.hdmi_in_crop_status_h_res_label.setText("NA")
        self.hdmi_in_crop_status_h_res_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))


        self.info_widget_layout.addWidget(self.hdmi_in_info_width_label, 0, 0)
        self.info_widget_layout.addWidget(self.hdmi_in_info_width_res_label, 0, 1)
        self.info_widget_layout.addWidget(self.hdmi_in_info_height_label, 0, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_info_height_res_label, 0, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_info_fps_label, 0, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_info_fps_res_label, 0, 5)

        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_label, 1, 0)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_x_label, 1, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_x_res_label, 1, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_y_label, 1, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_y_res_label, 1, 5)

        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_w_label, 2, 2)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_w_res_label, 2, 3)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_h_label, 2, 4)
        self.info_widget_layout.addWidget(self.hdmi_in_crop_status_h_res_label, 2, 5)


        # crop setting of hdmi in
        self.crop_setting_widget = QWidget(self.hdmi_in_widget)
        self.crop_setting_widget_layout = QGridLayout()
        self.crop_setting_widget.setLayout(self.crop_setting_widget_layout)

        self.hdmi_in_crop_x_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_x_label.setText("Crop Start X:")
        self.hdmi_in_crop_x_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_x_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_x_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_x_lineedit.setText("NA")
        self.hdmi_in_crop_x_lineedit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_y_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_y_label.setText("Crop Start Y:")
        self.hdmi_in_crop_y_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_y_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_y_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_y_lineedit.setText("NA")
        self.hdmi_in_crop_y_lineedit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_w_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_w_label.setText("Crop Width:")
        self.hdmi_in_crop_w_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_w_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_w_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_w_lineedit.setText("NA")
        self.hdmi_in_crop_w_lineedit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_h_label = QLabel(self.crop_setting_widget)
        self.hdmi_in_crop_h_label.setText("Crop Height:")
        self.hdmi_in_crop_h_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_h_lineedit = QLineEdit(self.crop_setting_widget)
        self.hdmi_in_crop_h_lineedit.setFixedWidth(100)
        self.hdmi_in_crop_h_lineedit.setText("NA")
        self.hdmi_in_crop_h_lineedit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.hdmi_in_crop_disable_btn = QPushButton(self.crop_setting_widget)
        self.hdmi_in_crop_disable_btn.setFixedWidth(100)
        self.hdmi_in_crop_disable_btn.setText("Disable")
        self.hdmi_in_crop_disable_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.hdmi_in_crop_disable_btn.clicked.connect(self.hdmi_in_crop_disable)

        self.hdmi_in_crop_enable_btn = QPushButton(self.crop_setting_widget)
        self.hdmi_in_crop_enable_btn.setFixedWidth(100)
        self.hdmi_in_crop_enable_btn.setText("Enable")
        self.hdmi_in_crop_enable_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
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
        self.brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.brightness_edit = QLineEdit(self.setting_widget)
        self.brightness_edit.setFixedWidth(100)
        self.brightness_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_brightness))
        self.brightness_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # contrast
        self.contrast_label = QLabel(self.setting_widget)
        self.contrast_label.setText("Contrast:")
        self.contrast_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.contrast_edit = QLineEdit(self.setting_widget)
        self.contrast_edit.setFixedWidth(100)
        self.contrast_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_contrast))
        self.contrast_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # red gain
        self.redgain_label = QLabel(self.setting_widget)
        self.redgain_label.setText("Red Gain:")
        self.redgain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.redgain_edit = QLineEdit(self.setting_widget)
        self.redgain_edit.setFixedWidth(100)
        self.redgain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_red_bias))
        self.redgain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # green gain
        self.greengain_label = QLabel(self.setting_widget)
        self.greengain_label.setText("Green Gain:")
        self.greengain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.greengain_edit = QLineEdit(self.setting_widget)
        self.greengain_edit.setFixedWidth(100)
        self.greengain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_green_bias))
        self.greengain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # blue gain
        self.blugain_label = QLabel(self.setting_widget)
        self.blugain_label.setText("Blue Gain:")
        self.blugain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.bluegain_edit = QLineEdit(self.setting_widget)
        self.bluegain_edit.setFixedWidth(100)
        self.bluegain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_blue_bias))
        self.bluegain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # client brightness adjust
        self.client_brightness_label = QLabel(self.setting_widget)
        self.client_brightness_label.setText("Client Br:")
        self.client_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_brightness_edit = QLineEdit(self.setting_widget)
        self.client_brightness_edit.setFixedWidth(100)
        self.client_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_brightness))
        self.client_brightness_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # client brightness adjust
        self.client_br_divisor_label = QLabel(self.setting_widget)
        self.client_br_divisor_label.setText("Client BrDivisor:")
        self.client_br_divisor_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_br_divisor_edit = QLineEdit(self.setting_widget)
        self.client_br_divisor_edit.setFixedWidth(100)
        self.client_br_divisor_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_br_divisor))
        self.client_br_divisor_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # client contrast(black level) adjust
        self.client_contrast_label = QLabel(self.setting_widget)
        self.client_contrast_label.setText("Client Black-Lv:")
        self.client_contrast_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_contrast_edit = QLineEdit(self.setting_widget)
        self.client_contrast_edit.setFixedWidth(100)
        self.client_contrast_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_contrast))
        self.client_contrast_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # client brightness mode adjust
        self.groupbox_client_brightness_method = QGroupBox("Client Brightness Method")
        self.groupbox_led_role_vboxlayout = QHBoxLayout()
        self.groupbox_client_brightness_method.setLayout(self.groupbox_led_role_vboxlayout)
        self.radiobutton_client_br_method_fix = QRadioButton("Fix Mode")
        self.radiobutton_client_br_method_fix.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_frame_brightness_mode_fix)
        self.radiobutton_client_br_method_fix.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.radiobutton_client_br_method_time = QRadioButton("Time Mode")
        self.radiobutton_client_br_method_time.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_frame_brightness_mode_time)
        self.radiobutton_client_br_method_time.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.radiobutton_client_br_method_als = QRadioButton("ALS Mode")
        self.radiobutton_client_br_method_als.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_frame_brightness_mode_als)
        self.radiobutton_client_br_method_als.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.radiobutton_client_br_method_test = QRadioButton("TEST Mode")
        self.radiobutton_client_br_method_test.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_frame_brightness_mode_test)
        self.radiobutton_client_br_method_test.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        log.debug("frame_brightness_algorithm : %d",
                  self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm)
        if self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm == frame_brightness_adjust.fix_mode:
            self.radiobutton_client_br_method_fix.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm == frame_brightness_adjust.auto_time_mode:
            self.radiobutton_client_br_method_time.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm == frame_brightness_adjust.auto_als_mode:
            self.radiobutton_client_br_method_als.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm == frame_brightness_adjust.test_mode:
            self.radiobutton_client_br_method_test.setChecked(True)
        self.groupbox_led_role_vboxlayout.addWidget(self.radiobutton_client_br_method_fix)
        self.groupbox_led_role_vboxlayout.addWidget(self.radiobutton_client_br_method_time)
        self.groupbox_led_role_vboxlayout.addWidget(self.radiobutton_client_br_method_als)
        self.groupbox_led_role_vboxlayout.addWidget(self.radiobutton_client_br_method_test)

        # sleep mode
        self.groupbox_sleep_mode = QGroupBox("Sleep Mode")
        self.groupbox_sleep_mode_vboxlayout = QHBoxLayout()
        self.groupbox_sleep_mode.setLayout(self.groupbox_sleep_mode_vboxlayout)
        self.radiobutton_sleep_mode_enable = QRadioButton("Enable")
        self.radiobutton_sleep_mode_enable.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_sleep_mode_enable
        )
        self.radiobutton_sleep_mode_disable = QRadioButton("Disable")
        self.radiobutton_sleep_mode_disable.clicked.connect(
            self.mainwindow.media_engine.media_processor.video_params.set_sleep_mode_disable
        )
        self.radiobutton_sleep_mode_enable.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.radiobutton_sleep_mode_disable.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        if self.mainwindow.media_engine.media_processor.video_params.sleep_mode_enable == 1:
            self.radiobutton_sleep_mode_enable.setChecked(True)
        if self.mainwindow.media_engine.media_processor.video_params.sleep_mode_enable == 0:
            self.radiobutton_sleep_mode_disable.setChecked(True)

        self.groupbox_sleep_mode_vboxlayout.addWidget(self.radiobutton_sleep_mode_enable)
        self.groupbox_sleep_mode_vboxlayout.addWidget(self.radiobutton_sleep_mode_disable)

        # target city
        self.combobox_target_city = QComboBox(self.mainwindow.right_frame)
        for city in City_Map:
            self.combobox_target_city.addItem(city.get("City"))
        self.combobox_target_city.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.combobox_target_city.setCurrentIndex(
            self.mainwindow.media_engine.media_processor.video_params.target_city_index
        )

        # client gamma adjust
        self.client_gamma_label = QLabel(self.setting_widget)
        self.client_gamma_label.setText("Client Gamma:")
        self.client_gamma_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_gamma_edit = QLineEdit(self.setting_widget)
        self.client_gamma_edit.setFixedWidth(100)
        self.client_gamma_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_gamma))
        self.client_gamma_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.client_day_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_day_mode_brightness_label.setText("Day Mode Br:")
        self.client_day_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_day_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_day_mode_brightness_edit.setFixedWidth(100)
        self.client_day_mode_brightness_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_day_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.day_mode_frame_brightness))

        self.client_night_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_night_mode_brightness_label.setText("Night Mode Br:")
        self.client_night_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_night_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_night_mode_brightness_edit.setFixedWidth(100)
        self.client_night_mode_brightness_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_night_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.night_mode_frame_brightness))

        self.client_sleep_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_sleep_mode_brightness_label.setText("Sleep Mode Br:")
        self.client_sleep_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_sleep_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_sleep_mode_brightness_edit.setFixedWidth(100)
        self.client_sleep_mode_brightness_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_sleep_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.sleep_mode_frame_brightness))

        self.video_params_confirm_btn = QPushButton(self.setting_widget)
        self.video_params_confirm_btn.setText("Set")
        self.video_params_confirm_btn.setFixedWidth(100)
        self.video_params_confirm_btn.clicked.connect(self.video_params_confirm_btn_clicked)
        self.video_params_confirm_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        # self.setting_widget_layout.addWidget(self.test_btn, 0, 0)
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

        self.setting_widget_layout.addWidget(self.client_brightness_label, 4, 4)
        self.setting_widget_layout.addWidget(self.client_brightness_edit, 4, 5)
        self.setting_widget_layout.addWidget(self.client_br_divisor_label, 2, 2)
        self.setting_widget_layout.addWidget(self.client_br_divisor_edit, 2, 3)
        self.setting_widget_layout.addWidget(self.client_contrast_label, 2, 0)
        self.setting_widget_layout.addWidget(self.client_contrast_edit, 2, 1)
        self.setting_widget_layout.addWidget(self.client_gamma_label, 2, 4)
        self.setting_widget_layout.addWidget(self.client_gamma_edit, 2, 5)

        self.setting_widget_layout.addWidget(self.groupbox_client_brightness_method, 4, 0, 2, 4)
        self.setting_widget_layout.addWidget(self.groupbox_sleep_mode, 7, 0, 2, 2)
        self.setting_widget_layout.addWidget(self.combobox_target_city, 7, 2, 0, 2)



        self.setting_widget_layout.addWidget(self.client_day_mode_brightness_label, 9, 0)
        self.setting_widget_layout.addWidget(self.client_day_mode_brightness_edit, 9, 1)
        self.setting_widget_layout.addWidget(self.client_night_mode_brightness_label, 9, 2)
        self.setting_widget_layout.addWidget(self.client_night_mode_brightness_edit, 9, 3)
        self.setting_widget_layout.addWidget(self.client_sleep_mode_brightness_label, 9, 4)
        self.setting_widget_layout.addWidget(self.client_sleep_mode_brightness_edit, 9, 5)
        self.setting_widget_layout.addWidget(self.video_params_confirm_btn, 5, 5)

        self.hdmi_in_layout.addWidget(self.preview_widget)
        self.hdmi_in_layout.addWidget(self.info_widget)
        self.hdmi_in_layout.addWidget(self.crop_setting_widget)
        self.hdmi_in_layout.addWidget(self.setting_widget)
        
        # hdmi-in preview cast type, now we use v4l2loopback kernel module to show preview status
        self.hdmi_in_cast_type = "v4l2"

        self.cv2camera = None
        self.preview_count = 0
        # for preview use /dev/video3~5 (generated by v4l2loopback module)
        # It changes every time you open the preview function
        self.cv2_preview_v4l2_sink = None
        self.video6_check_count = 0
        self.cv2_check_count = 0
        self.v4l2loopback_dev_open_count = 0
        self.preview_mutex = QMutex()
        self.preview_videosink_check_count = 0
        self.check_tc358743_interval = 2000
        self.check_tc358743_timer = QTimer(self)
        self.check_tc358743_timer.timeout.connect(self.check_tc358743_timer_event)
        # self.going_to_open_preview = False # 如果True則表示目前頁面處於hdmi-in, 因為一進來hdmi-in頁面就要開始preview
        self.check_tc358743_timer.start(self.check_tc358743_interval)

        self.tc358743 = TC358743()
        self.tc358743.signal_refresh_tc358743_param.connect(self.refresh_tc358743_param)
        self.tc358743.get_tc358743_dv_timing()
        self.media_engine.media_processor.signal_play_hdmi_in_start_ret.connect(
            self.play_hdmi_in_start_ret)
        self.media_engine.media_processor.signal_play_hdmi_in_finish_ret.connect(
            self.play_hdmi_in_finish_ret)

        # If Once hdmi-in start streaming to led, play_hdmi_in_status is True
        # If stop_send_to_led is called, play_hdmi_in_status is False
        self.play_hdmi_in_status = False

    def combobox_target_city_changed(self, index):
        log.debug("index = %d", index)
        self.mainwindow.media_engine.media_processor.video_params.set_target_city_index(index)

    def combobox_target_city_change(self, index):
        self.combobox_target_city.setCurrentIndex(index)

    def radiobutton_client_br_method_fix_mode_set(self):
        self.radiobutton_client_br_method_fix.click()

    def radiobutton_client_br_method_time_mode_set(self):
        self.radiobutton_client_br_method_time.click()

    def radiobutton_client_br_method_als_mode_set(self):
        self.radiobutton_client_br_method_als.click()

    def radiobutton_client_br_method_test_mode_set(self):
        self.radiobutton_client_br_method_test.click()

    def radiobutton_sleep_mode_disable_set(self):
        self.radiobutton_sleep_mode_disable.click()

    def radiobutton_sleep_mode_enable_set(self):
        self.radiobutton_sleep_mode_enable.click()

    def check_tc358743_timer_event(self):

        self.preview_mutex.lock()
        if self.mainwindow.page_idx != page_hdmi_in_content_idx:
            # log.debug("Not in hdmi-in page")
            self.preview_mutex.unlock()
            return
        tmp_preview_status = self.preview_status
        self.preview_mutex.unlock()
        log.debug("****tmp_preview_status : %d*********", tmp_preview_status)
        try:
            if self.tc358743.get_tc358743_hdmi_connected_status() is True:
                if self.tc358743.set_tc358743_dv_bt_timing() is True:
                    self.tc358743.reinit_tc358743_dv_timing()
                self.start_hdmi_in_preview()
        except Exception as e:
            log.debug(e)


    def start_hdmi_in_preview(self):
        self.preview_mutex.lock()
        if self.preview_status is True:
            log.debug("self.preview_status is True")
            self.preview_mutex.unlock()
            return
        # p = Popen("modprobe v4l2loopback video_nr=3,4,5,6", shell=True, stdout=PIPE)
        if self.cv2camera is not None:
            log.debug("cv2 camera is going to quit")
            # do we need a wait for save exit a qthread @20221013
            # self.cv2camera.release_cam()
            self.cv2camera.quit()
            # do we need a wait for save exit a qthread @20221013
            # self.cv2camera.wait()
            self.cv2camera = None
        # check previous ffmpeg cast process
        if self.ffmpy_hdmi_in_cast_process is not None:
            os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
        else:
            # find any ffmpeg process
            p = os.popen("pgrep ffmpeg").read()
            log.debug("pgrep ffmpeg, res = %s", p)
            log.debug("p.len() = %d", len(p))
            if len(p) != 0:
                log.fatal("still got ffmpeg process")
                k = os.popen("pkill ffmpeg")
                k.close()
        # add for check again for save @20221013
        self.tc358743.get_tc358743_hdmi_connected_status()

        if self.tc358743.hdmi_connected is False:
            pass
        else:
            if self.ffmpy_hdmi_in_cast_process is None:
                if self.hdmi_in_cast_type == "v4l2":
                    self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_v4l2()
                else:
                    self.ffmpy_hdmi_in_cast_process = self.start_hdmi_in_cast_h264()

            if self.ffmpy_hdmi_in_cast_process is not None:
                preview_videosink_check_count = 0
                for i in range(100):
                    video_src_ok = self.check_video_src_is_ok(self.cv2_preview_v4l2_sink)
                    preview_videosink_check_count = i
                    if video_src_ok == 0:
                        # log.debug("check /dev/video6 status count : %d", i)
                        break
                if preview_videosink_check_count > self.preview_videosink_check_count:
                    self.preview_videosink_check_count = preview_videosink_check_count
                    log.debug("self.preview_videosink_check_count = %d", self.preview_videosink_check_count)
                if self.cv2camera is None:
                    self.cv2camera = CV2Camera(self.cv2_preview_v4l2_sink, self.hdmi_in_cast_type)
                    self.cv2camera.signal_get_rawdata.connect(self.getRaw)
                else:
                    log.debug("Still got cv2camera")
                # self.cv2camera.open()  # 影像讀取功能開啟
                self.cv2camera.start()  # 在子緒啟動影像讀取
                # self.cv2camera.exec()
                self.cv2camera.set_hdmi_in_cast(True)
                self.preview_status = True
        self.preview_mutex.unlock()

        if self.ffmpy_hdmi_in_cast_process is not None:
            self.cast_pid_label.setText("ff cast pid:" + str(self.ffmpy_hdmi_in_cast_process.pid))
        else:
            self.cast_pid_label.setText("ff cast pid:None")

    def stop_hdmi_in_preview(self):
        log.debug("")
        self.preview_mutex.lock()

        if self.cv2camera is not None:
            self.cv2camera.close_tc358743_cam()
            self.cv2camera.close()  # 關閉
        log.debug("start to check cv2camera status")
        cv2_check_count = 0

        while True:
            if self.cv2camera is None:
                break
            time.sleep(0.05)
            if self.cv2camera.isRunning() == 0 and self.cv2camera.isFinished() == 1:
                # pass
                self.cv2camera.quit()
                self.cv2camera = None
                break
            else:
                cv2_check_count += 1
                if cv2_check_count > 10:
                    log.fatal("cv2 hang")
                    log.debug("self.cv2_check_count :%d", self.cv2_check_count)
                    log.debug("max /dev/video6 status count : %d", self.video6_check_count)
                    break
                # log.debug("cv2 is running: %d", self.cv2camera.isRunning())
                # log.debug("cv2 is Finished: %d", self.cv2camera.isFinished())
        if cv2_check_count > self.cv2_check_count:
            self.cv2_check_count = cv2_check_count
        log.debug("self.cv2_check_count :%d", self.cv2_check_count)
        self.stop_hdmi_in_cast()
        # p = Popen("modprobe -rf v4l2loopback", shell=True, stdout=PIPE)
        self.preview_status = False
        self.preview_mutex.unlock()

        if self.ffmpy_hdmi_in_cast_process is not None:
            self.cast_pid_label.setText("ff cast pid:" + str(self.ffmpy_hdmi_in_cast_process.pid))
        else:
            self.cast_pid_label.setText("ff cast pid:None")


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

    def select_preview_v4l2_device(self):
        num = self.preview_count % 3
        self.preview_count += 1
        if num == 0:
            self.cv2_preview_v4l2_sink = "/dev/video3"
            return ["/dev/video3", "/dev/video6"]
        elif num == 1:
            self.cv2_preview_v4l2_sink = "/dev/video4"
            return ["/dev/video4", "/dev/video6"]
        elif num == 2:
            self.cv2_preview_v4l2_sink = "/dev/video5"
            return ["/dev/video5", "/dev/video6"]

        '''for i in range(3, 5):
            v4l2_dev = None
            v4l2_dev_node = "/dev/video" + str(i)
            log.debug("v4l2_dev = %s", v4l2_dev_node)
            try:
                v4l2_dev = open(v4l2_dev_node)
            except Exception as e:
                log.debug("%s open fail", v4l2_dev_node)

            if v4l2_dev is not None:
                v4l2_dev.close()
                break

        return v4l2_dev_node'''

    def start_hdmi_in_cast_v4l2(self):
        # choose a stable v4l2loopback device to be a sink
        hdmi_in_cast_out = self.select_preview_v4l2_device()

        ffmpy_hdmi_in_cast_process = self.media_engine.start_hdmi_in_v4l2("/dev/video0", hdmi_in_cast_out)
        if ffmpy_hdmi_in_cast_process is None:
            log.debug("ffmpy_hdmi_in_cast_process is None")
            self.preview_label.setText("Please Check HDMI-in Dongle")
        else:
            log.debug("ffmpy_hdmi_in_cast_process is alive")
            self.preview_label.setText("Please Wait for signal")

        return ffmpy_hdmi_in_cast_process

    def stop_hdmi_in_cast(self):
        try:
            if self.ffmpy_hdmi_in_cast_process is not None:
                os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
            else:
                log.debug("self.ffmpy_hdmi_in_cast_process is None")
                p = os.popen("pgrep ffmpeg").read()
                if p is not None:
                    log.fatal("still got ffmpeg process")
                    k = os.popen("pkill ffmpeg")
                    k.close()
        except Exception as e:
            log.debug(e)

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
        if video_params.frame_brightness != int(self.client_brightness_edit.text()):
            log.debug("frame_brightness changed!")
            # media_processor.set_frame_brightness_value(int(self.client_brightness_edit.text()))
        if video_params.frame_br_divisor != int(self.client_br_divisor_edit.text()):
            log.debug("frame_br_divisor changed!")
            # media_processor.set_frame_br_divisor_value(int(self.client_br_divisor_edit.text()))
        if video_params.frame_contrast != int(self.client_contrast_edit.text()):
            log.debug("frame_contrast changed!")
            # media_processor.set_frame_contrast_value(int(self.client_contrast_edit.text()))
        if video_params.frame_gamma != float(self.client_gamma_edit.text()):
            log.debug("frame_gamma changed!")
            # media_processor.set_frame_gamma_value(float(self.client_gamma_edit.text()))

        clients = self.mainwindow.clients
        if video_params.frame_brightness != int(self.client_brightness_edit.text()):
            # video_params.frame_brightness = int(self.client_brightness_edit.text())
            media_processor.set_frame_brightness_value(int(self.client_brightness_edit.text()))
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_frame_brightness,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_brightness))

        if video_params.frame_br_divisor != int(self.client_br_divisor_edit.text()):
            # video_params.frame_br_divisor = int(self.client_br_divisor_edit.text())
            media_processor.set_frame_br_divisor_value(int(self.client_br_divisor_edit.text()))
            for c in clients:
                c.send_cmd(cmd_set_frame_br_divisor,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_br_divisor))

        if video_params.frame_contrast != int(self.client_contrast_edit.text()):
            # video_params.frame_contrast = int(self.client_contrast_edit.text())
            media_processor.set_frame_contrast_value(int(self.client_contrast_edit.text()))
            for c in clients:
                c.send_cmd(cmd_set_frame_contrast,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_contrast))

        if video_params.frame_gamma != float(self.client_gamma_edit.text()):
            # video_params.frame_gamma = float(self.client_gamma_edit.text())
            media_processor.set_frame_gamma_value(float(self.client_gamma_edit.text()))
            for c in clients:
                c.send_cmd(cmd_set_frame_gamma,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_gamma))

    def send_to_led_depreciated(self):
        log.debug("")
        if self.media_engine.media_processor.play_single_file_worker is not None:
            print("before play_single_file_worker.get_task_status() = ", self.media_engine.media_processor.play_single_file_worker.get_task_status())
            log.debug("play single file stop")
            self.media_engine.resume_play()
            self.media_engine.stop_play()

        if self.media_engine.media_processor.play_playlist_worker is not None:
            print("before play_playlist_worker.get_task_status() = ", self.media_engine.media_processor.play_playlist_worker.get_task_status())
            log.debug("play playlist stop")
            self.media_engine.resume_play()
            self.media_engine.stop_play()
        if self.media_engine.media_processor.play_hdmi_in_worker is not None: 
            print("play_hdmi_in_worker.get_task_status() = ", self.media_engine.media_processor.play_hdmi_in_worker.get_task_status())

        print("ffmpy_process=", self.media_engine.media_processor.ffmpy_process)
        # if self.media_engine.media_processor.ffmpy_process is None:
        if self.media_engine.media_processor.play_hdmi_in_worker is None:
            log.debug("Start streaming to led")
            video_src = "/dev/video6"
            streaming_sink = [udp_sink]
            self.media_engine.media_processor.hdmi_in_play(video_src, streaming_sink)
        else:
            log.debug("Stop streaming to led")
            self.media_engine.stop_play()
            # self.media_engine.media_processor.play_hdmi_in_worker.stop()
            # del self.media_engine.media_processor.play_hdmi_in_worker
            # self.media_engine.media_processor.play_hdmi_in_worker = None

    def send_to_led_parser(self):
        if "Start" in self.play_action_btn.text():
            self.start_send_to_led()
        elif "Pause" in self.play_action_btn.text():
            self.media_engine.pause_play()
            self.play_action_btn.setText("Resume")
            self.hdmi_in_play_status_label.setText("Streaming-Pause")
        elif "Resume" in self.play_action_btn.text():
            self.media_engine.resume_play()
            self.play_action_btn.setText("Pause")
            self.hdmi_in_play_status_label.setText("Streaming")

    def start_send_to_led(self):
        video_src_ok = -1
        video6_check_count = 0
        for i in range(100):
            video_src_ok = self.check_video_src_is_ok("/dev/video6")
            video6_check_count = i
            if video_src_ok == 0:
                # log.debug("check /dev/video6 status count : %d", i)
                break
            # time.sleep(1)
        if video6_check_count > self.video6_check_count:
            self.video6_check_count = video6_check_count
        self.v4l2loopback_dev_open_count += 1
        log.debug("check /dev/video6 status count : %d", video6_check_count)
        log.debug("max /dev/video6 status count : %d", self.video6_check_count)
        log.debug("v4l2loopback device open count: %d", self.v4l2loopback_dev_open_count)
        if video_src_ok != 0: # /dev/video6 is not ok!
            log.fatal("video_src got some problems")
            # log.debug("re-start preview in v4l2")
            # check ffmpy hdmi-in cast process
            '''if self.cv2camera is not None:
                self.cv2camera.close_tc358743_cam()
                self.cv2camera.close()  # 關閉
            while True:
                if self.cv2camera.isRunning() == 0 and self.cv2camera.isFinished() == 1:
                    # pass
                    break
                else:
                    log.debug("cv2 is running: %d", self.cv2camera.isRunning())
                    log.debug("cv2 is Finished: %d", self.cv2camera.isFinished())
            
            self.stop_hdmi_in_cast()
            self.start_hdmi_in_preview()'''
            return
        self.media_engine.resume_play()
        self.media_engine.stop_play()
        if self.media_engine.media_processor.play_hdmi_in_worker is None:
            log.debug("Start streaming to led")
            video_src = "/dev/video6"
            streaming_sink = [udp_sink]
            self.media_engine.media_processor.hdmi_in_play(video_src, streaming_sink)

        self.play_hdmi_in_status = True

    def pause_send_to_led(self):
        log.debug("")
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            log.debug("hdmi-in worker is alive")
            self.media_engine.pause_play()

    def stop_send_to_led(self):
        log.debug("Stop streaming to led")
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            self.media_engine.resume_play()
            self.media_engine.stop_play()
        self.play_hdmi_in_status = False

    def stop_hdmi_in_streaming(self):
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            log.debug("Stop streaming to led")
            self.media_engine.resume_play()
            self.media_engine.stop_play()

    def play_hdmi_in_start_ret(self):
        log.debug("")
        self.play_action_btn.setText("Pause")
        self.hdmi_in_play_status_label.setText("Streaming")
        self.ffmpy_pid_label.setText("ffmpy pid:" + str(self.media_engine.media_processor.ffmpy_process.pid))

    def play_hdmi_in_finish_ret(self):
        log.debug("")
        self.play_action_btn.setText("Start Play")
        self.hdmi_in_play_status_label.setText("Non-Streaming")
        self.ffmpy_pid_label.setText("ffmpy pid:None")

    def cv2_read_or_open_fail(self):
        # handle re-init tc358743
        '''log.debug("")
        if self.ffmpy_hdmi_in_cast_process is not None:
            self.media_engine.media_processor.play_hdmi_in_work.force_stop = True
            os.kill(self.ffmpy_hdmi_in_cast_process.pid, signal.SIGTERM)
            self.ffmpy_hdmi_in_cast_process = None'''

        # Stop send_to_led first
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            log.debug("Stop streaming to led")
            self.media_engine.resume_play()
            self.media_engine.stop_play()


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
            else:
                log.debug("set_tc358743_dv_bt_timing is False")

    def refresh_tc358743_param(self, connected, width, height, fps):
        log.debug("connected = %d", connected)
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
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
                self.hdmi_in_crop_x_lineedit.setText(str(video_params.get_hdmi_in_crop_start_x()))
                self.hdmi_in_crop_y_lineedit.setText(str(video_params.get_hdmi_in_crop_start_y()))
                self.hdmi_in_crop_w_lineedit.setText(str(video_params.get_hdmi_in_crop_w()))
                self.hdmi_in_crop_h_lineedit.setText(str(video_params.get_hdmi_in_crop_h()))

            if self.play_hdmi_in_status is True:
                log.debug("play_hdmi_in_status is True, Need to do something to reopen the streaming")

        else:
            self.hdmi_in_crop_status_x_res_label.setText("0")
            self.hdmi_in_crop_status_y_res_label.setText("0")
            self.hdmi_in_crop_status_w_res_label.setText(str(self.tc358743.hdmi_width))
            self.hdmi_in_crop_status_h_res_label.setText(str(self.tc358743.hdmi_height))
            self.hdmi_in_crop_x_lineedit.setText(str(video_params.get_hdmi_in_crop_start_x()))
            self.hdmi_in_crop_y_lineedit.setText(str(video_params.get_hdmi_in_crop_start_y()))
            self.hdmi_in_crop_w_lineedit.setText(str(video_params.get_hdmi_in_crop_w()))
            self.hdmi_in_crop_h_lineedit.setText(str(video_params.get_hdmi_in_crop_h()))
            self.stop_hdmi_in_preview()
            self.preview_label.setText("HDMI-in Signal Lost")
            if self.play_hdmi_in_status is True:
                log.debug("play_hdmi_in_status is True, Need to do something to re-start preview")

    def hdmi_in_crop_disable(self):
        self.b_hdmi_in_crop_enable = False
        self.video_crop_disable()

    def hdmi_in_crop_enable(self):
        log.debug("")
        self.b_hdmi_in_crop_enable = True
        self.video_crop_enable()

    def video_crop_enable(self):
        log.debug("crop_enable")
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
        if video_params.hdmi_in_crop_start_x != int(self.hdmi_in_crop_x_lineedit.text()):
            media_processor.set_hdmi_in_crop_start_x_value(int(self.hdmi_in_crop_x_lineedit.text()))
        if video_params.hdmi_in_crop_start_y != int(self.hdmi_in_crop_y_lineedit.text()):
            media_processor.set_hdmi_in_crop_start_y_value(int(self.hdmi_in_crop_y_lineedit.text()))
        if video_params.hdmi_in_crop_w != int(self.hdmi_in_crop_w_lineedit.text()):
            media_processor.set_hdmi_in_crop_w_value(int(self.hdmi_in_crop_w_lineedit.text()))
        if video_params.hdmi_in_crop_h != int(self.hdmi_in_crop_h_lineedit.text()):
            media_processor.set_hdmi_in_crop_h_value(int(self.hdmi_in_crop_h_lineedit.text()))

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
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
        if video_params.hdmi_in_crop_start_x != int(self.hdmi_in_crop_x_lineedit.text()):
            media_processor.set_hdmi_in_crop_start_x_value(int(self.hdmi_in_crop_x_lineedit.text()))
        if video_params.hdmi_in_crop_start_y != int(self.hdmi_in_crop_y_lineedit.text()):
            media_processor.set_hdmi_in_crop_start_y_value(int(self.hdmi_in_crop_y_lineedit.text()))
        if video_params.hdmi_in_crop_w != int(self.hdmi_in_crop_w_lineedit.text()):
            media_processor.set_hdmi_in_crop_w_value(int(self.hdmi_in_crop_w_lineedit.text()))
        if video_params.hdmi_in_crop_h != int(self.hdmi_in_crop_h_lineedit.text()):
            media_processor.set_hdmi_in_crop_h_value(int(self.hdmi_in_crop_h_lineedit.text()))
        if self.media_engine.media_processor.play_hdmi_in_worker is not None:
            utils.ffmpy_utils.ffmpy_crop_disable(self.mainwindow.led_wall_width,
                                                 self.mainwindow.led_wall_height)

    def check_video_src_is_ok(self, video_src):
        res = -1
        cmd = "ffprobe -hide_banner" + " " + video_src
        # ffprobe_res = os.popen(cmd).read()
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        ffprobe_stdout, ffprobe_stderr = p.communicate()

        '''log.debug("++++++++++++")
        log.debug("ffprobe_stdout : %s", ffprobe_stdout.decode())
        log.debug("ffprobe_stderr : %s", ffprobe_stderr.decode())
        log.debug("------------")'''
        p.kill()
        if "Stream" in ffprobe_stderr.decode():
            log.debug("%s is ready", video_src)
            res = 0
        else:
            pass
            # log.debug("%s is not ready", video_src)

        return res

'''
class CheckVideoSrcThread(QThread):
    def __init__(self, video_src):
        super().__init__()
        self.video_src = video_src

    def run(self):
        video_src_ok = -1
        for i in range(3):
            log.debug('WorkerThread::run %s' + str(i))
            time.sleep(0.5)
            video_src_ok = self.check_video_src_is_ok()
            if video_src_ok == 0:
                break

    def check_video_src_is_ok(self):
        res = -1
        cmd = "ffprobe" + " " + self.video_src
        ffprobe_res = os.popen(cmd).read()
        if "Invalid argument" in ffprobe_res:
            log.debug("%s is not ready", self.video_src)
        else:
            log.debug("%s is ready", self.video_src)
            res = 0
        return res'''
