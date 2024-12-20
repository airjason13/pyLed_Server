import subprocess
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt, QThread, QMutex, QTimer
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
from str_define import *
from subprocess import PIPE, Popen
import hashlib

from global_def import *


class CmsPage(QObject):

	def __init__(self, mainwindow, **kwargs):
		super(CmsPage, self).__init__(**kwargs)

		self.mainwindow = mainwindow
		self.media_engine = mainwindow.media_engine
		self.mainwindow.right_frame = mainwindow.right_frame

		self.cms_widget = QWidget(self.mainwindow.right_frame)
		self.mainwindow.right_layout.addWidget(self.cms_widget)
		self.cms_widget_layout = QGridLayout()
		self.btn_start_play_cms = QPushButton(self.cms_widget)
		self.btn_start_play_cms.setText("Start Playing CMS")
		self.btn_start_play_cms.setFixedWidth(240)
		self.btn_start_play_cms.setFont(QFont(qfont_style_default, qfont_style_size_medium))
		self.btn_start_play_cms.clicked.connect(self.start_play_cms)

		self.btn_stop_play_cms = QPushButton(self.cms_widget)
		self.btn_stop_play_cms.setText("Stop Playing CMS")
		self.btn_stop_play_cms.setFixedWidth(240)
		self.btn_stop_play_cms.setFont(QFont(qfont_style_default, qfont_style_size_medium))
		self.btn_stop_play_cms.clicked.connect(self.stop_play_cms)

		self.cms_widget_layout.addWidget(self.btn_start_play_cms, 0, 1)
		self.cms_widget_layout.addWidget(self.btn_stop_play_cms, 0, 2)

		self.cms_widget.setLayout(self.cms_widget_layout)

		self.browser_process = None

		self.x_padding = 4
		self.y_padding = 29
		self.chromium_pos_x = 10
		self.chromium_pos_y = 10
		self.chromium_width = 640
		self.chromium_height = 480


	def launch_chromium(self):
		try:
			#subprocess.Popen("ifconfig enp1s0u1u4 up", shell=True)
			#time.sleep(5)
			if self.browser_process is not None:
				os.kill(self.browser_process.pid, signal.SIGTERM)
				self.browser_process = None
			'''sandbox_param = "--no-sandbox --test-type --disable-audio-output --mute-audio "
			autoplay_param = "--autoplay-policy=no-user-gesture-required "
			window_size_param = "--window-size=" + str(self.chromium_width) + "," + str(self.chromium_height) + " "
			window_pos_param = "--window-position=" + str(self.chromium_pos_x) + "," + str(self.chromium_pos_y) + " "
			
			file_uri = "http://icast.tw/icast/educ/"
			open_chromium_cmd = "/usr/bin/chromium " + sandbox_param +autoplay_param + window_size_param + window_pos_param + \
			                    autoplay_param + "--app=" + file_uri'''
			open_chromium_cmd = "speedup_chromium.sh &"
			self.browser_process = subprocess.Popen(open_chromium_cmd, shell=True)
			log.debug("self.browser_process.pid = %d", self.browser_process.pid)
		except Exception as e:
			log.error(e)

	def start_play_cms(self):
		subprocess.Popen("pkill chromium", shell=True)

		time.sleep(5) # self.launch_chromium()
		self.launch_chromium()
		self.media_engine.resume_play()
		self.media_engine.stop_play()
		if self.media_engine.media_processor.play_cms_worker is None:
			log.debug("Start streaming to led")
			self.media_engine.media_processor.cms_play(self.chromium_width, self.chromium_height,
			                                           self.chromium_pos_x + self.x_padding + 1,
			                                           self.chromium_pos_y + self.y_padding, udp_sink)

	def stop_play_cms(self):
		try:
			subprocess.Popen("pkill chromium", shell=True)
			if self.browser_process is not None:
				os.kill(self.browser_process.pid, signal.SIGTERM)
				self.browser_process = None
			self.media_engine.resume_play()
			self.media_engine.stop_play()

		except Exception as e:
			log.error(e)
