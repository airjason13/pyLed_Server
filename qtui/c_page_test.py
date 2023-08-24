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

class TestPage(QObject):
	def __init__(self, mainwindow, **kwargs):
		super(TestPage, self).__init__(**kwargs)

		self.mainwindow = mainwindow
		self.media_engine = mainwindow.media_engine
		self.mainwindow.right_frame = mainwindow.right_frame

		self.reboot_test_count = 0

		''' Start of UI layout'''
		self.test_widget = QWidget(self.mainwindow.right_frame)
		self.mainwindow.right_layout.addWidget(self.test_widget)
		self.test_widget_layout = QGridLayout()

		self.label_test_reboot = QLabel(self.test_widget)
		self.label_test_reboot.setText("Count of Test Clients")
		self.label_test_reboot.setFixedWidth(240)
		self.label_test_reboot.setFont(QFont(qfont_style_default, qfont_style_size_medium))

		self.lineedit_test_reboot_client_count = QLineEdit(self.test_widget)
		self.lineedit_test_reboot_client_count.setText("2")
		self.lineedit_test_reboot_client_count.setFixedWidth(240)
		self.lineedit_test_reboot_client_count.setFont(QFont(qfont_style_default, qfont_style_size_medium))

		self.btn_start_test_reboot = QPushButton(self.test_widget)
		self.btn_start_test_reboot.setText("Start Test Reboot")
		self.btn_start_test_reboot.setFixedWidth(240)
		self.btn_start_test_reboot.setFont(QFont(qfont_style_default, qfont_style_size_medium))
		self.btn_start_test_reboot.clicked.connect(self.start_test_reboot)

		self.btn_stop_test_reboot = QPushButton(self.test_widget)
		self.btn_stop_test_reboot.setText("Stop Test Reboot")
		self.btn_stop_test_reboot.setFixedWidth(240)
		self.btn_stop_test_reboot.setFont(QFont(qfont_style_default, qfont_style_size_medium))
		self.btn_stop_test_reboot.clicked.connect(self.stop_test_reboot)

		self.label_test_reboot_count_prefix = QLabel(self.test_widget)
		self.label_test_reboot_count_prefix.setText("Reboot TEST Count:")
		self.label_test_reboot_count_prefix.setFixedWidth(240)
		self.label_test_reboot_count_prefix.setFont(QFont(qfont_style_default, qfont_style_size_medium))

		self.label_test_reboot_count = QLabel(self.test_widget)
		self.label_test_reboot_count.setText(str(self.reboot_test_count))
		self.label_test_reboot_count.setFixedWidth(240)
		self.label_test_reboot_count.setFont(QFont(qfont_style_default, qfont_style_size_medium))

		self.test_widget_layout.addWidget(self.label_test_reboot, 0, 1)
		self.test_widget_layout.addWidget(self.lineedit_test_reboot_client_count, 1, 1)
		self.test_widget_layout.addWidget(self.btn_start_test_reboot, 1, 2)
		self.test_widget_layout.addWidget(self.btn_stop_test_reboot, 1, 3)
		self.test_widget_layout.addWidget(self.label_test_reboot_count_prefix, 2, 1)
		self.test_widget_layout.addWidget(self.label_test_reboot_count, 2, 2)

		self.test_widget.setLayout(self.test_widget_layout)
		self.reboot_client_count = int(self.lineedit_test_reboot_client_count.text())

		''' End of UI layout'''
		'''Start of function definition'''
		self.reboot_check_timer = QTimer(self)
		self.reboot_check_timer.timeout.connect(self.reboot_check)

	def start_test_reboot(self):
		log.debug("start_test_reboot")
		self.reboot_client_count = int(self.lineedit_test_reboot_client_count.text())
		log.debug("self.reboot_client_count = %d", self.reboot_client_count)
		try:
			self.reboot_check_timer.start(30*1000) # 30 secs
		except Exception as e:
			log.debug(e)

	def stop_test_reboot(self):
		log.debug("stop_test_reboot")
		self.reboot_check_timer.stop()

	def reboot_check(self):
		log.debug("reboot_check_timer")
		log.debug("len(self.mainwindow.clients) : %d", len(self.mainwindow.clients))
		log.debug("self.reboot_client_count : %d", self.reboot_client_count)
		if len(self.mainwindow.clients) == self.reboot_client_count:
			log.debug("got target!")
			time.sleep(20)
			# add the reboot_test_count
			self.reboot_test_count += 1
			self.label_test_reboot_count.setText(str(self.reboot_test_count))
			# trigger the client reboot
			self.mainwindow.client_reboot_flags = True
			try:
				for i in range(10):
					self.mainwindow.server_broadcast_client_reboot()
					time.sleep(0.1)
			except Exception as e:
				log.debug(e)
			self.mainwindow.client_reboot_flags = False


