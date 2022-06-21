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

log = utils.log_utils.logging_init(__file__)


class CmsPage(QObject):

	def __init__(self, mainwindow, **kwargs):
		super(CmsPage, self).__init__(**kwargs)

		self.mainwindow = mainwindow
		self.media_engine = mainwindow.media_engine
		self.mainwindow.right_frame = mainwindow.right_frame

		self.cms_widget = QWidget(self.mainwindow.right_frame)
		self.mainwindow.right_layout.addWidget(self.cms_widget)
		self.cms_widget_layout = QGridLayout()
		self.btn_test_cms = QPushButton(self.cms_widget)
		self.btn_test_cms.setText("Start Test CMS")
		self.btn_test_cms.clicked.connect(self.start_play_cms)
		self.cms_widget_layout.addWidget(self.btn_test_cms, 0, 1)

		self.cms_widget.setLayout(self.cms_widget_layout)

		self.browser_process = None

	def launch_chromium(self):
		try:
			if self.browser_process is not None:
				os.kill(self.browser_process.pid, signal.SIGTERM)
				self.browser_process = None
			autoplay_param = "--autoplay-policy=no-user-gesture-required "
			window_size_param = "--window-size=320,240 "
			window_pos_param = "--window-position=10,10 "
			file_uri = "/home/venom/LocalHtmlTest/index.html"
			open_chromium_cmd = "/usr/bin/chromium " + window_size_param + window_pos_param + \
			                    autoplay_param + "--app=file://" + file_uri
			self.browser_process = subprocess.Popen(open_chromium_cmd, shell=True)
			log.debug("self.browser_process.pid = %d", self.browser_process.pid)
		except Exception as e:
			log.error(e)

	def start_play_cms(self):
		self.launch_chromium()

		self.media_engine.stop_play()
		if self.media_engine.media_processor.play_cms_worker is None:
			log.debug("Start streaming to led")

			self.media_engine.media_processor.cms_play( 320,240, 10, 10, udp_sink)


