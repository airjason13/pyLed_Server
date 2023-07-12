from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont
from PyQt5.QtWidgets import QTreeWidget, QTableWidget, QWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, \
                            QTreeWidgetItem, QPushButton, QHBoxLayout, QMenu, QAction, QGroupBox, QVBoxLayout, \
                            QRadioButton, QComboBox
from g_defs.c_TreeWidgetItemSP import CTreeWidget
import os
from global_def import *
from set_qstyle import *
from c_new_playlist_dialog import NewPlaylistDialog
from commands_def import *
import utils.log_utils
import utils.ffmpy_utils
import utils.file_utils
import hashlib
from str_define import *
from astral_hashmap import *
log = utils.log_utils.logging_init(__file__)

class media_page(QObject):
    signal_refresh_internal_medialist = pyqtSignal()
    media_btn_width = 180
    media_btn_height = 30
    ICLED_CURRENT_GAIN_FUNCTION = True

    def __init__(self, mainwindow, **kwargs):
        super(media_page, self).__init__(**kwargs)
        self.mainwindow = mainwindow
        self.media_engine = mainwindow.media_engine
        self.play_option_repeat = self.mainwindow.play_option_repeat
        self.file_tree = CTreeWidget(self.mainwindow.right_frame)

        self.file_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_tree.setColumnCount(1)
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.headerItem().setText(0, "Media Files")
        font = QFont()
        font.setPointSize(24)
        self.file_tree.setFont(font)
        # Add Internal Media Folder in tree root
        self.right_clicked_select_file_uri = None
        self.NewPlaylistDialog = None

        self.internal_media_root = QTreeWidgetItem(self.file_tree)

        self.internal_media_root.setText(0, "Internal Media")
        for f in self.mainwindow.media_engine.internal_medialist.filelist:
            internal_file_item = QTreeWidgetItem()
            internal_file_item.setText(0, os.path.basename(f))
            # utils.ffmpy_utils.gen_webp_from_video(internal_media_folder, os.path.basename(f))  # need to remove later
            utils.ffmpy_utils.gen_webp_from_video_threading(internal_media_folder, os.path.basename(f))
            self.internal_media_root.addChild(internal_file_item)

        self.file_tree.addTopLevelItem(self.internal_media_root)

        # Add External Media Folder in tree root
        self.external_media_root = QTreeWidgetItem(self.file_tree)
        self.external_media_root.setText(0, "External Media")  # + ":" + external_media_list.folder_uri)
        child_count = 0
        for external_media_list in self.mainwindow.media_engine.external_medialist:
            external_folder = QTreeWidgetItem()
            external_folder.setText(0, os.path.basename(external_media_list.folder_uri))
            self.external_media_root.addChild(external_folder)
            for f in external_media_list.filelist:
                external_file_item = QTreeWidgetItem()
                external_file_item.setText(0, os.path.basename(f))
                # utils.ffmpy_utils.gen_webp_from_video(external_media_list.folder_uri,
                #                                      os.path.basename(f))  # need to remove later
                utils.ffmpy_utils.gen_webp_from_video_threading(external_media_list.folder_uri, os.path.basename(f))
                self.external_media_root.child(child_count).addChild(external_file_item)
            child_count += 1
            # self.external_media_root_list.append(external_media_root)
        self.file_tree.addTopLevelItem(self.external_media_root)

        # playlist file tree
        self.qtw_media_play_list = QTreeWidgetItem(self.file_tree)
        self.qtw_media_play_list.setText(0, "Playlist")
        for playlist in self.mainwindow.media_engine.playlist:
            playlist_root = QTreeWidgetItem(self.qtw_media_play_list)
            playlist_root.setText(0, playlist.name)
            for file_name in playlist.fileslist:
                #log.debug("playlist.fileslist :%s", file_name)
                file_name_item = QTreeWidgetItem(playlist_root)
                file_name_item.setText(0, os.path.basename(file_name))
                playlist_root.addChild(file_name_item)

        self.file_tree.addTopLevelItem(self.qtw_media_play_list)
        self.file_tree.expandAll()

        self.file_tree.setMouseTracking(True)
        # Add right clicked function signal/slot
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.menu_context_tree)

        log.debug("mount point : %s", utils.file_utils.get_mount_points())

        self.play_option_init()
        self.video_params_option_init()

        self.file_tree_widget = QWidget(self.mainwindow.right_frame)
        file_tree_layout = QVBoxLayout()
        self.file_tree_widget.setLayout(file_tree_layout)
        file_tree_layout.addWidget(self.file_tree)
        file_tree_layout.addWidget(self.play_option_widget)
        file_tree_layout.addWidget(self.video_params_widget)
        self.file_tree_widget.setMouseTracking(True)
        self.file_tree.mouseMove.connect(self.mainwindow.media_page_mousemove)
        self.mainwindow.right_layout.addWidget(self.file_tree_widget)

        self.signal_refresh_internal_medialist.connect(self.mainwindow.internaldef_medialist_changed)

    def refresh_internal_medialist(self):
        log.debug("start to check playlist")
        utils.file_utils.sync_playlist()
        self.media_engine.sync_playlist()
        # print( self.mainwindow.media_engine.playlist)
        for i in reversed(range(self.internal_media_root.childCount())):
            # log.debug("self.medialist_page.internal_media_root.child() = %s",
            #          self.internal_media_root.child(i).text(0))
            self.internal_media_root.removeChild(self.internal_media_root.child(i))

        self.internal_media_root.setText(0, "Internal Media")
        for f in self.mainwindow.media_engine.internal_medialist.filelist:
            internal_file_item = QTreeWidgetItem()
            internal_file_item.setText(0, os.path.basename(f))
            # utils.ffmpy_utils.gen_webp_from_video(internal_media_folder, os.path.basename(f))  # need to remove later
            utils.ffmpy_utils.gen_webp_from_video_threading(internal_media_folder, os.path.basename(f))
            self.internal_media_root.addChild(internal_file_item)
        self.refresh_playlist_items()

    def refresh_playlist_items(self):
        for i in reversed(range(self.qtw_media_play_list.childCount())):
            self.qtw_media_play_list.removeChild(self.qtw_media_play_list.child(i))
        for playlist in self.mainwindow.media_engine.playlist:
            log.debug("playlist = %s", playlist)
            playlist_root = QTreeWidgetItem(self.qtw_media_play_list)
            playlist_root.setText(0, playlist.name)
            for file_name in playlist.fileslist:
                #log.debug("playlist.fileslist :%s", file_name)
                file_name_item = QTreeWidgetItem(playlist_root)
                file_name_item.setText(0, os.path.basename(file_name))
                playlist_root.addChild(file_name_item)



    def play_option_init(self):
        """play singal file btn"""
        self.btn_play_select_file = QPushButton(self.mainwindow.right_frame)
        self.btn_play_select_file.setText("Play Select File")
        self.btn_play_select_file.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        # self.btn_play_select_file.setFixedWidth(media_btn_width)
        self.btn_play_select_file.setFixedSize(self.media_btn_width, self.media_btn_height)
        self.btn_play_select_file.setDisabled(True)

        """play playlist btn"""
        self.btn_play_playlist = QPushButton(self.mainwindow.right_frame)
        self.btn_play_playlist.setText("Play Playlist")
        # self.btn_play_playlist.setFixedWidth(media_btn_width)
        self.btn_play_playlist.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.btn_play_playlist.setFixedSize(self.media_btn_width, self.media_btn_height)
        # if len(self.media_play_list) == 0:
        #    self.btn_play_playlist.setDisabled(True)
        self.btn_play_playlist.clicked.connect(self.mainwindow.play_playlist_trigger)

        """stop btn"""
        self.btn_stop = QPushButton(self.mainwindow.right_frame)
        self.btn_stop.setText("Stop")
        # self.btn_stop.setFixedWidth(media_btn_width)
        self.btn_stop.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.btn_stop.setFixedSize(self.media_btn_width, self.media_btn_height)
        self.btn_stop.clicked.connect(self.stop_media_trigger)
        self.btn_stop.clicked.connect(self.mainwindow.stop_media_set)

        self.btn_pause = QPushButton(self.mainwindow.right_frame)
        self.btn_pause.setText("Pause")
        self.btn_pause.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.btn_pause.setFixedSize(self.media_btn_width, self.media_btn_height)
        # self.btn_pause.setFixedWidth(media_btn_width)
        self.btn_pause.clicked.connect(self.pause_media_trigger)

        self.btn_repeat = QPushButton(self.mainwindow.right_frame)
        if self.mainwindow.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.mainwindow.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.mainwindow.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")

        # self.btn_repeat.setFixedWidth(media_btn_width)
        self.btn_repeat.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.btn_repeat.setFixedSize(self.media_btn_width, self.media_btn_height)
        self.btn_repeat.clicked.connect(self.repeat_option_trigger)

        self.play_option_widget = QWidget(self.mainwindow.right_frame)
        play_option_layout = QHBoxLayout()
        self.play_option_widget.setLayout(play_option_layout)
        play_option_layout.addWidget(self.btn_play_select_file)
        play_option_layout.addWidget(self.btn_play_playlist)
        play_option_layout.addWidget(self.btn_stop)
        play_option_layout.addWidget(self.btn_pause)
        play_option_layout.addWidget(self.btn_repeat)

    def video_params_option_init(self):
        # brightness
        self.brightness_label = QLabel(self.mainwindow.right_frame)
        self.brightness_label.setText("Brightness:")
        self.brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.brightness_edit.setFixedWidth(100)
        self.brightness_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_brightness))

        # contrast
        self.contrast_label = QLabel(self.mainwindow.right_frame)
        self.contrast_label.setText("Contrast:")
        self.contrast_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.contrast_edit.setFixedWidth(100)
        self.contrast_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_contrast))

        # contrast
        self.image_period_label = QLabel(self.mainwindow.right_frame)
        self.image_period_label.setText("Image Period:")
        self.image_period_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.image_period_edit = QLineEdit(self.mainwindow.right_frame)
        self.image_period_edit.setFixedWidth(100)
        self.image_period_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.image_period))

        # red gain
        self.redgain_label = QLabel(self.mainwindow.right_frame)
        self.redgain_label.setText("Red Gain:")
        self.redgain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.redgain_edit = QLineEdit(self.mainwindow.right_frame)
        self.redgain_edit.setFixedWidth(100)
        self.redgain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_red_bias))

        # green gain
        self.greengain_label = QLabel(self.mainwindow.right_frame)
        self.greengain_label.setText("Green Gain:")
        self.greengain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.greengain_edit = QLineEdit(self.mainwindow.right_frame)
        self.greengain_edit.setFixedWidth(100)
        self.greengain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_green_bias))

        # blue gain
        self.blugain_label = QLabel(self.mainwindow.right_frame)
        self.blugain_label.setText("Blue Gain:")
        self.blugain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.bluegain_edit = QLineEdit(self.mainwindow.right_frame)
        self.bluegain_edit.setFixedWidth(100)
        self.bluegain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_blue_bias))

        #client brightness mode adjust
        self.groupbox_client_brightness_method = QGroupBox("Client Brightness Method")
        # self.groupbox_client_brightness_method.setFont(QFont(qfont_style_default, qfont_style_size_medium))
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
        if self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm \
                == frame_brightness_adjust.fix_mode:
            self.radiobutton_client_br_method_fix.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm \
                == frame_brightness_adjust.auto_time_mode:
            self.radiobutton_client_br_method_time.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm \
                == frame_brightness_adjust.auto_als_mode:
            self.radiobutton_client_br_method_als.setChecked(True)
        elif self.mainwindow.media_engine.media_processor.video_params.frame_brightness_algorithm \
                == frame_brightness_adjust.test_mode:
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
            self.mainwindow.media_engine.media_processor.set_sleep_mode_enable
        )
        self.radiobutton_sleep_mode_disable = QRadioButton("Disable")
        self.radiobutton_sleep_mode_disable.clicked.connect(
            self.mainwindow.media_engine.media_processor.set_sleep_mode_disable
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
        self.combobox_target_city.currentIndexChanged.connect(self.combobox_target_city_changed)

        # client brightness adjust
        self.client_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_brightness_label.setText("Client Br:")
        self.client_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_brightness_edit.setFixedWidth(100)
        self.client_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_brightness))

        self.client_day_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_day_mode_brightness_label.setText("Day Mode Br:")
        self.client_day_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_day_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_day_mode_brightness_edit.setFixedWidth(100)
        self.client_day_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.day_mode_frame_brightness))

        self.client_night_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_night_mode_brightness_label.setText("Night Mode Br:")
        self.client_night_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_night_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_night_mode_brightness_edit.setFixedWidth(100)
        self.client_night_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.night_mode_frame_brightness))

        self.client_sleep_mode_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_sleep_mode_brightness_label.setText("Sleep Mode Br:")
        self.client_sleep_mode_brightness_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_sleep_mode_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_sleep_mode_brightness_edit.setFixedWidth(100)
        self.client_sleep_mode_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.sleep_mode_frame_brightness))

        # client brightness divisor adjust
        self.client_br_divisor_label = QLabel(self.mainwindow.right_frame)
        self.client_br_divisor_label.setText("Client BrDivisor:")
        self.client_br_divisor_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_br_divisor_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_br_divisor_edit.setFixedWidth(100)
        self.client_br_divisor_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_br_divisor))

        # client contrast(black level) adjust
        self.client_contrast_label = QLabel(self.mainwindow.right_frame)
        self.client_contrast_label.setText("Client Black-Lv:")
        self.client_contrast_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_contrast_edit.setFixedWidth(100)
        self.client_contrast_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_contrast))

        # client gamma adjust
        self.client_gamma_label = QLabel(self.mainwindow.right_frame)
        self.client_gamma_label.setText("Client Gamma:")
        self.client_gamma_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_gamma_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_gamma_edit.setFixedWidth(100)
        self.client_gamma_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_gamma))

        self.video_params_widget = QWidget(self.mainwindow.right_frame)
        video_params_layout = QGridLayout()
        self.video_params_widget.setLayout(video_params_layout)

        self.video_params_confirm_btn = QPushButton(self.mainwindow.right_frame)
        self.video_params_confirm_btn.setText("Set")
        self.video_params_confirm_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_confirm_btn.setFixedWidth(150)
        self.video_params_confirm_btn.clicked.connect(self.video_params_confirm_btn_clicked)

        self.video_params_pinch_btn = QPushButton(self.mainwindow.right_frame)
        self.video_params_pinch_btn.setText("P5")
        self.video_params_pinch_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_pinch_btn.setFixedWidth(150)
        self.video_params_pinch_btn.clicked.connect(self.video_params_pinch_btn_clicked)

        #crop params
        self.video_params_crop_x_label = QLabel(self.mainwindow.right_frame)
        self.video_params_crop_x_label.setText("Crop_Start_X:")
        self.video_params_crop_x_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_x_label.setFixedWidth(160)

        self.video_params_crop_x_edit = QLineEdit(self.mainwindow.right_frame)
        self.video_params_crop_x_edit.setText(str(self.media_engine.media_processor.video_params.crop_start_x))
        self.video_params_crop_x_edit.setFixedWidth(100)

        self.video_params_crop_y_label = QLabel(self.mainwindow.right_frame)
        self.video_params_crop_y_label.setText("Crop_Start_Y:")
        self.video_params_crop_y_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_y_label.setFixedWidth(160)

        self.video_params_crop_y_edit = QLineEdit(self.mainwindow.right_frame)
        self.video_params_crop_y_edit.setText(str(self.media_engine.media_processor.video_params.crop_start_y))
        self.video_params_crop_y_edit.setFixedWidth(100)

        self.video_params_crop_w_label = QLabel(self.mainwindow.right_frame)
        self.video_params_crop_w_label.setText("Crop_W:")
        self.video_params_crop_w_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_w_label.setFixedWidth(160)

        self.video_params_crop_w_edit = QLineEdit(self.mainwindow.right_frame)
        self.video_params_crop_w_edit.setText(str(self.media_engine.media_processor.video_params.crop_w))
        self.video_params_crop_w_edit.setFixedWidth(100)

        self.video_params_crop_h_label = QLabel(self.mainwindow.right_frame)
        self.video_params_crop_h_label.setText("Crop_H:")
        self.video_params_crop_h_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_h_label.setFixedWidth(160)

        self.video_params_crop_h_edit = QLineEdit(self.mainwindow.right_frame)
        self.video_params_crop_h_edit.setText(str(self.media_engine.media_processor.video_params.crop_h))
        self.video_params_crop_h_edit.setFixedWidth(100)

        self.video_params_crop_enable = QPushButton(self.mainwindow.right_frame)
        self.video_params_crop_enable.setText("Crop Enable")
        self.video_params_crop_enable.setFixedWidth(150)
        self.video_params_crop_enable.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_enable.clicked.connect(self.video_crop_enable)

        self.video_params_crop_disable = QPushButton(self.mainwindow.right_frame)
        self.video_params_crop_disable.setText("Crop Disable")
        self.video_params_crop_disable.setFixedWidth(150)
        self.video_params_crop_disable.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.video_params_crop_disable.clicked.connect(self.video_crop_disable)

        if self.ICLED_CURRENT_GAIN_FUNCTION:
            '''For ICLed Type and Current Gain'''
            self.client_icled_type_label = QLabel(self.mainwindow.right_frame)
            self.client_icled_type_label.setText("ICLed Type:")
            self.client_icled_type_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_type_label.setFixedWidth(160)

            self.client_icled_type_combobox = QComboBox(self.mainwindow.right_frame)
            self.client_icled_type_combobox.addItems([ICLED_TYPE_AOS, ICLED_TYPE_ANAPEX])
            icled_type = utils.file_utils.get_led_type_config()
            if ICLED_TYPE_AOS in icled_type:
                self.client_icled_type_combobox.setCurrentText(ICLED_TYPE_AOS)
            else:
                self.client_icled_type_combobox.setCurrentText(ICLED_TYPE_ANAPEX)
            self.client_icled_type_combobox.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_type_combobox.setFixedWidth(320)

            self.clent_icled_red_current_gain_label = QLabel(self.mainwindow.right_frame)
            self.clent_icled_red_current_gain_label.setText("Red C Gain:")
            self.clent_icled_red_current_gain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.clent_icled_red_current_gain_label.setFixedWidth(160)
            self.client_icled_red_current_gain_edit = QLineEdit(self.mainwindow.right_frame)
            self.client_icled_red_current_gain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_red_current_gain_edit.setText(utils.file_utils.get_red_current_gain_from_config())
            self.client_icled_red_current_gain_edit.setFixedWidth(80)

            self.clent_icled_green_current_gain_label = QLabel(self.mainwindow.right_frame)
            self.clent_icled_green_current_gain_label.setText("Green C Gain:")
            self.clent_icled_green_current_gain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.clent_icled_green_current_gain_label.setFixedWidth(160)
            self.client_icled_green_current_gain_edit = QLineEdit(self.mainwindow.right_frame)
            self.client_icled_green_current_gain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_green_current_gain_edit.setText(utils.file_utils.get_green_current_gain_from_config())
            self.client_icled_green_current_gain_edit.setFixedWidth(80)

            self.clent_icled_blue_current_gain_label = QLabel(self.mainwindow.right_frame)
            self.clent_icled_blue_current_gain_label.setText("Blue C Gain:")
            self.clent_icled_blue_current_gain_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.clent_icled_blue_current_gain_label.setFixedWidth(160)
            self.client_icled_blue_current_gain_edit = QLineEdit(self.mainwindow.right_frame)
            self.client_icled_blue_current_gain_edit.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_blue_current_gain_edit.setText(utils.file_utils.get_green_current_gain_from_config())
            self.client_icled_blue_current_gain_edit.setFixedWidth(80)

            self.client_icled_type_check_btn = QPushButton(self.mainwindow.right_frame)
            self.client_icled_type_check_btn.setText("Set ICLED TYPE")
            self.client_icled_type_check_btn.setFixedWidth(260)
            self.client_icled_type_check_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_type_check_btn.clicked.connect(self.client_set_icled_type)

            self.client_icled_cgain_check_btn = QPushButton(self.mainwindow.right_frame)
            self.client_icled_cgain_check_btn.setText("Set C-Gain")
            self.client_icled_cgain_check_btn.setFixedWidth(160)
            self.client_icled_cgain_check_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))
            self.client_icled_cgain_check_btn.clicked.connect(self.client_set_icled_current_gain)

        video_params_layout.addWidget(self.redgain_label, 0, 0)
        video_params_layout.addWidget(self.redgain_edit, 0, 1)
        video_params_layout.addWidget(self.greengain_label, 0, 2)
        video_params_layout.addWidget(self.greengain_edit, 0, 3)
        video_params_layout.addWidget(self.blugain_label, 0, 4)
        video_params_layout.addWidget(self.bluegain_edit, 0, 5)

        video_params_layout.addWidget(self.brightness_label, 1, 0)
        video_params_layout.addWidget(self.brightness_edit, 1, 1)
        video_params_layout.addWidget(self.contrast_label, 1, 2)
        video_params_layout.addWidget(self.contrast_edit, 1, 3)
        video_params_layout.addWidget(self.image_period_label, 1, 4)
        video_params_layout.addWidget(self.image_period_edit, 1, 5)

        video_params_layout.addWidget(self.groupbox_client_brightness_method, 2, 0, 7, 4)
        video_params_layout.addWidget(self.client_gamma_label, 5, 4)
        video_params_layout.addWidget(self.client_gamma_edit, 5, 5)
        video_params_layout.addWidget(self.client_brightness_label, 6, 4)
        video_params_layout.addWidget(self.client_brightness_edit, 6, 5)

        video_params_layout.addWidget(self.groupbox_sleep_mode, 10, 0, 3, 3)
        video_params_layout.addWidget(self.combobox_target_city, 10, 4)

        video_params_layout.addWidget(self.client_day_mode_brightness_label, 13, 0)
        video_params_layout.addWidget(self.client_day_mode_brightness_edit, 13, 1)
        video_params_layout.addWidget(self.client_night_mode_brightness_label, 13, 2)
        video_params_layout.addWidget(self.client_night_mode_brightness_edit, 13, 3)
        video_params_layout.addWidget(self.client_sleep_mode_brightness_label, 13, 4)
        video_params_layout.addWidget(self.client_sleep_mode_brightness_edit, 13, 5)

        video_params_layout.addWidget(self.client_br_divisor_label, 14, 2)
        video_params_layout.addWidget(self.client_br_divisor_edit, 14, 3)
        video_params_layout.addWidget(self.client_contrast_label, 14, 0)
        video_params_layout.addWidget(self.client_contrast_edit, 14, 1)


        #crop
        video_params_layout.addWidget(self.video_params_crop_x_label, 15, 0)
        video_params_layout.addWidget(self.video_params_crop_x_edit, 15, 1)
        video_params_layout.addWidget(self.video_params_crop_y_label, 15, 2)
        video_params_layout.addWidget(self.video_params_crop_y_edit, 15, 3)
        video_params_layout.addWidget(self.video_params_crop_w_label, 16, 0)
        video_params_layout.addWidget(self.video_params_crop_w_edit, 16, 1)
        video_params_layout.addWidget(self.video_params_crop_h_label, 16, 2)
        video_params_layout.addWidget(self.video_params_crop_h_edit, 16, 3)
        video_params_layout.addWidget(self.video_params_crop_enable, 16, 5)
        video_params_layout.addWidget(self.video_params_crop_disable, 16, 4)
        if self.ICLED_CURRENT_GAIN_FUNCTION:
            '''ICLED TYPE and Current Gain'''
            video_params_layout.addWidget(self.client_icled_type_label, 17, 0)
            video_params_layout.addWidget(self.client_icled_type_combobox, 17, 1)

            video_params_layout.addWidget(self.client_icled_type_check_btn, 17, 3, 1, 4)
            video_params_layout.addWidget(self.client_icled_cgain_check_btn, 17, 5)
            video_params_layout.addWidget(self.clent_icled_red_current_gain_label, 18, 0)
            video_params_layout.addWidget(self.client_icled_red_current_gain_edit, 18, 1)
            video_params_layout.addWidget(self.clent_icled_green_current_gain_label, 18, 2)
            video_params_layout.addWidget(self.client_icled_green_current_gain_edit, 18, 3)
            video_params_layout.addWidget(self.clent_icled_blue_current_gain_label, 18, 4)
            video_params_layout.addWidget(self.client_icled_blue_current_gain_edit, 18, 5)

        video_params_layout.addWidget(self.video_params_pinch_btn, 14, 4)
        video_params_layout.addWidget(self.video_params_confirm_btn, 14, 5)

        if self.mainwindow.engineer_mode is True:
            self.max_brightness_label = QLabel(self.mainwindow.right_frame)
            self.max_brightness_label.setText( "Max Frame Brightness Value is " +
                str((256*int(self.client_brightness_edit.text()))/(int(self.client_br_divisor_edit.text())*100)))
            video_params_layout.addWidget(self.max_brightness_label, 4, 0, 1, 5)

    def combobox_target_city_changed(self, index):
        log.debug("index = %d", index)
        self.mainwindow.media_engine.media_processor.video_params.set_target_city_index(index)

    def combobox_target_city_change(self, index):
        self.combobox_target_city.setCurrentIndex(index)

    def radiobutton_sleep_mode_disable_set(self):
        self.radiobutton_sleep_mode_disable.click()

    def radiobutton_sleep_mode_enable_set(self):
        self.radiobutton_sleep_mode_enable.click()

    def radiobutton_client_br_method_fix_mode_set(self):
        self.radiobutton_client_br_method_fix.click()

    def radiobutton_client_br_method_time_mode_set(self):
        self.radiobutton_client_br_method_time.click()

    def radiobutton_client_br_method_als_mode_set(self):
        self.radiobutton_client_br_method_als.click()

    def radiobutton_client_br_method_test_mode_set(self):
        self.radiobutton_client_br_method_test.click()

    def stop_media_trigger(self):
        log.debug("")

    def pause_media_trigger(self):
        """check the popen subprocess is alive or not"""
        if self.mainwindow.media_engine.media_processor.play_status == play_status.playing:
            self.mainwindow.pause_media_set()
            self.btn_pause.setText("Resume")
        elif self.mainwindow.media_engine.media_processor.play_status == play_status.pausing:
            self.mainwindow.resume_media_set()
            self.btn_pause.setText("Pause")

    def repeat_option_trigger(self):
        if self.play_option_repeat >= repeat_option.repeat_option_max:
            self.play_option_repeat = repeat_option.repeat_none
        else:
            self.play_option_repeat += 1

        if self.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.play_option_repeat == repeat_option.repeat_random:
            self.btn_repeat.setText("Random")
        elif self.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")

        self.mainwindow.repeat_option_set(self.play_option_repeat)
        log.debug("self.play_option_repeat : %d", self.play_option_repeat)

    # right clicked slot function
    def menu_context_tree(self, position):
        widgetitem = self.file_tree.itemAt(position)
        self.right_clicked_pos = position
        if widgetitem.childCount() != 0:
            ''' parent 為 Playlist,表示自己為playlist之一'''
            if widgetitem.parent().text(0) == "Playlist":
                self.show_playlist_pop_menu(self.file_tree.mapToGlobal(position))
                return
            log.debug("Just a label, not file list")
            return
        if widgetitem.parent() is not None:
            if widgetitem.parent().text(0) == "Internal Media":
                self.right_clicked_select_file_uri = internal_media_folder + "/" + widgetitem.text(0)
            elif widgetitem.parent().text(0) == "External Media":
                log.debug("%s", widgetitem.text(0))
                return
            elif "Playlist" in widgetitem.parent().text(0):
                self.show_playlist_pop_menu(self.file_tree.mapToGlobal(position))
                return
            elif widgetitem.parent().parent() is not None:
                log.debug("%s", widgetitem.parent().parent().text(0))
                if "External Media" in widgetitem.parent().parent().text(0):
                    for external_medialist in self.media_engine.external_medialist:
                        if widgetitem.parent().text(0) in external_medialist.folder_uri:
                            for file_uri in external_medialist.filelist:
                                if widgetitem.text(0) in file_uri:
                                    self.right_clicked_select_file_uri = file_uri

                elif "Playlist" in widgetitem.parent().parent().text(0):
                    log.debug("no playlist right click")
                    # self.right_clicked_pos = position
                    self.show_playlist_file_pop_menu(self.file_tree.mapToGlobal(position))

                    return
        else:
            log.debug("root")
            return

        self.show_media_file_pop_menu(self.file_tree.mapToGlobal(position))

    def show_media_file_pop_menu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)

        play_act = QAction("Play", self)
        pop_menu.addAction(play_act)

        del_act = QAction("Delete", self)
        pop_menu.addAction(del_act)

        # remove crop function in separate files
        # crop_act = QAction("Crop", self)
        # crop_act.setDisabled(True)
        # pop_menu.addAction(crop_act)
        pop_menu.addSeparator()

        add_to_playlist_menu = QMenu('AddtoPlaylist')
        set_qstyle_dark(add_to_playlist_menu)

        for playlist in self.mainwindow.media_engine.playlist:
            playlist_name = playlist.name
            add_to_playlist_menu.addAction('add to ' + playlist_name)

        add_to_playlist_menu.addAction('add to new playlist')
        pop_menu.addMenu(add_to_playlist_menu)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(pos)

    '''處理playlist'''
    def show_playlist_pop_menu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)
        playact = QAction("Play Playlist", self)
        pop_menu.addAction(playact)
        remove_act = QAction("Remove Playlist", self)
        pop_menu.addAction(remove_act)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)
        pop_menu.exec_(pos)

    def show_playlist_file_pop_menu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)

        remove_act = QAction("Remove file from playlist", self)
        pop_menu.addAction(remove_act)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(pos)

    def pop_menu_trigger_act(self, q):
        log.debug("%s", q.text())
        if q.text() == "Play":
            """play single file"""
            log.debug("file_uri :%s", self.right_clicked_select_file_uri)
            self.media_engine.play_single_file(self.right_clicked_select_file_uri)
            '''self.ff_process = utils.ffmpy_utils.ffmpy_execute(self, self.right_clicked_select_file_uri, width=80, height=96)
            self.play_type = play_type.play_single'''
        elif "add to " in q.text():
            log.debug("media file uri : %s", self.right_clicked_select_file_uri)
            playlist_name = q.text().split(" ")[2]
            if playlist_name == 'new':
                # launch a dialog
                # pop up a playlist generation dialog
                if self.NewPlaylistDialog is None:
                    self.NewPlaylistDialog = NewPlaylistDialog(self.mainwindow.media_engine.playlist)
                self.NewPlaylistDialog.signal_new_playlist_generate.connect(self.mainwindow.slot_new_playlist)
                self.NewPlaylistDialog.show()
            else:
                self.mainwindow.media_engine.add_to_playlist(playlist_name, self.right_clicked_select_file_uri)
        elif q.text() == "Remove file from playlist":
            # log.debug("%s", self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y()).text(0))
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            parent = item.parent()
            remove_file_name = item.text(0)
            remove_from_playlist = parent.text(0)
            log.debug("remove_file_name : %s", remove_file_name)
            log.debug("remove_from_playlist : %s", remove_from_playlist)
            for i in range(parent.childCount()):
                if parent.child(i).text(0) == remove_file_name:
                    self.mainwindow.media_engine.remove_from_playlist(remove_from_playlist, i)
                    break
        elif q.text() == "Remove Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            remove_playlist_name = item.text(0)
            self.mainwindow.media_engine.del_playlist(remove_playlist_name)
        elif q.text() == "Play Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            play_playlist_name = item.text(0)
            self.mainwindow.media_engine.play_playlist(play_playlist_name)
        elif q.text() == "Delete":
            log.debug("file_uri :%s", self.right_clicked_select_file_uri)
            # remove file and thumbnail file
            file_ui = self.right_clicked_select_file_uri.replace(" ", "\ ")
            if os.path.exists(self.right_clicked_select_file_uri) is True:
                os.remove(self.right_clicked_select_file_uri)
            log.debug("self.right_clicked_select_file_uri.split(internal_media_folder)[1] = %s", self.right_clicked_select_file_uri.split(internal_media_folder +"/")[1]);
            thumbnail_file_name = hashlib.md5(
                self.right_clicked_select_file_uri.split(internal_media_folder + "/")[1].split(".")[0].encode('utf-8')).hexdigest() + ".webp"

            thumbnail_file = internal_media_folder + ThumbnailFileFolder + thumbnail_file_name
            log.debug("thumbnail_file = %s", thumbnail_file)
            if os.path.exists(thumbnail_file) is True:
                log.debug("thumbnail_file exists")
                os.remove(self.right_clicked_select_file_uri)
            self.signal_refresh_internal_medialist.emit()

    def resfresh_video_params_config_file(self):
        log.debug("")
        self.media_engine.media_processor.video_params.refresh_config_file()

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
        if video_params.image_period != int(self.image_period_edit.text()):
            log.debug("image period changed!")
            media_processor.set_image_period_value(int(self.image_period_edit.text()))

        clients = self.mainwindow.clients
        if video_params.frame_brightness != int(self.client_brightness_edit.text()):
            # video_params.frame_brightness = int(self.client_brightness_edit.text())
            media_processor.set_frame_brightness_value(int(self.client_brightness_edit.text()))
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_frame_brightness,
                           self.mainwindow.cmd_seq_id_increase(),
                            str(video_params.frame_brightness))

        #day mode brightness
        if video_params.day_mode_frame_brightness != int(self.client_day_mode_brightness_edit.text()):
            media_processor.set_day_mode_frame_brightness_value(int(self.client_day_mode_brightness_edit.text()))

        # night mode brightness
        if video_params.night_mode_frame_brightness != int(self.client_night_mode_brightness_edit.text()):
            media_processor.set_night_mode_frame_brightness_value(int(self.client_night_mode_brightness_edit.text()))

        # sleep mode brightness
        if video_params.sleep_mode_frame_brightness != int(self.client_sleep_mode_brightness_edit.text()):
            media_processor.set_sleep_mode_frame_brightness_value(
                int(self.client_sleep_mode_brightness_edit.text()))

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

        if self.mainwindow.engineer_mode is True:
            self.refresh_max_brightness_label()

    def video_params_pinch_btn_clicked(self):
        log.debug("")
        clients = self.mainwindow.clients
        if self.video_params_pinch_btn.text() == "P5":
            self.video_params_pinch_btn.setText("P10")
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_pixel_interval,
                           self.mainwindow.cmd_seq_id_increase(),
                            str(1))
        else:
            self.video_params_pinch_btn.setText("P5")
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_pixel_interval,
                           self.mainwindow.cmd_seq_id_increase(), str(0))

    def video_crop_enable(self):
        log.debug("crop_enable")
        # test
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
        if video_params.crop_start_x != int(self.video_params_crop_x_edit.text()):
            media_processor.set_crop_start_x_value(int(self.video_params_crop_x_edit.text()))

        if video_params.crop_start_y != int(self.video_params_crop_y_edit.text()):
            media_processor.set_crop_start_y_value(int(self.video_params_crop_y_edit.text()))

        if video_params.crop_w != int(self.video_params_crop_w_edit.text()):
            media_processor.set_crop_w_value(int(self.video_params_crop_w_edit.text()))

        if video_params.crop_h != int(self.video_params_crop_h_edit.text()):
            media_processor.set_crop_h_value(int(self.video_params_crop_h_edit.text()))

        if self.media_engine.media_processor.ffmpy_process is not None:
            utils.ffmpy_utils.ffmpy_crop_enable(self.video_params_crop_x_edit.text(),
                                         self.video_params_crop_y_edit.text(),
                                         self.video_params_crop_w_edit.text(),
                                         self.video_params_crop_h_edit.text(),
                                         self.mainwindow.led_wall_width,
                                         self.mainwindow.led_wall_height)

    def video_crop_disable(self):
        log.debug("crop_disable")
        media_processor = self.media_engine.media_processor
        self.video_params_crop_x_edit.setText("0")
        self.video_params_crop_y_edit.setText("0")
        self.video_params_crop_w_edit.setText("0")
        self.video_params_crop_h_edit.setText("0")
        media_processor.set_crop_start_x_value(int(self.video_params_crop_x_edit.text()))
        media_processor.set_crop_start_y_value(int(self.video_params_crop_y_edit.text()))
        media_processor.set_crop_w_value(int(self.video_params_crop_w_edit.text()))
        media_processor.set_crop_h_value(int(self.video_params_crop_h_edit.text()))

        if self.media_engine.media_processor.ffmpy_process is not None:
            utils.ffmpy_utils.ffmpy_crop_disable(self.mainwindow.led_wall_width,
                                        self.mainwindow.led_wall_height)

    def refresh_max_brightness_label(self):
        if self.mainwindow.engineer_mode is False:
            return
        self.max_brightness_label.setText("Max Frame Brightness Value is " +
                                          str((256 * int(self.client_brightness_edit.text())) / (
                                                      int(self.client_br_divisor_edit.text()) * 100)))



    def client_set_icled_type(self):
        root_dir = os.path.dirname(sys.modules['__main__'].__file__)
        led_config_dir = os.path.join(root_dir, 'video_params_config')

        str_ret = self.client_icled_type_combobox.currentText()
        log.debug(str_ret)
        # log.debug("video_params file is %s: ", os.path.join(led_config_dir, ".video_params_config"))
        if os.path.exists(os.path.join(led_config_dir, ".icled_type_config")) is False:
            utils.file_utils.init_led_type_config()

        utils.file_utils.set_led_type_config(self.client_icled_type_combobox.currentText())

        # icled_type = self.client_icled_type_combobox.currentText()
        self.mainwindow.icled_type = utils.file_utils.get_led_type_config()
        # send command to client for sync
        clients = self.mainwindow.clients
        for c in clients:
            #log.debug("c.client_ip = %s", c.client_ip)
            c.send_cmd(cmd_set_frame_brightness,
                       self.mainwindow.cmd_seq_id_increase(),
                       self.mainwindow.icled_type)

        
    def client_set_icled_current_gain(self):
        root_dir = os.path.dirname(sys.modules['__main__'].__file__)
        led_config_dir = os.path.join(root_dir, 'video_params_config')

        str_ret = self.client_icled_type_combobox.currentText()
        log.debug(str_ret)

        if os.path.exists(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
            utils.file_utils.init_icled_current_gain_params_config()

        utils.file_utils.set_rgb_current_gain_to_config(self.client_icled_red_current_gain_edit.text(),
                                                        self.client_icled_green_current_gain_edit.text(),
                                                        self.client_icled_blue_current_gain_edit.text())

        '''cmd_params = "rgain=" + utils.file_utils.get_red_current_gain_from_config() + "," + \
                     "ggain=" + utils.file_utils.get_green_current_gain_from_config() + "," + \
                     "bgain=" + utils.file_utils.get_blue_current_gain_from_config()'''

        self.mainwindow.current_gain_cmd_params = \
            "rgain=" + utils.file_utils.get_red_current_gain_from_config() + "," + \
            "ggain=" + utils.file_utils.get_green_current_gain_from_config() + "," + \
            "bgain=" + utils.file_utils.get_blue_current_gain_from_config()
        log.debug("self.mainwindow.current_gain_cmd_params = %s", self.mainwindow.current_gain_cmd_params)
        # send command to client for sync
        clients = self.mainwindow.clients
        for c in clients:
            #log.debug("c.client_ip = %s", c.client_ip)
            c.send_cmd(cmd_set_icled_current_gain,
                       self.mainwindow.cmd_seq_id_increase(),
                       self.mainwindow.current_gain_cmd_params)
