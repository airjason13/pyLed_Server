import platform
import os
import signal
import threading
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout, QVBoxLayout,
                            QGridLayout, QFrame,QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                            QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
                             QFileDialog, QListWidget, QFileSystemModel, QTreeView, QMenu, QAction, QAbstractItemView,)
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QMovie
from PyQt5.QtCore import Qt, QMutex, pyqtSlot
import pyqtgraph as pg
import qdarkstyle, requests, sys, time, random, json, datetime, re
import socket
from time import sleep
from global_def import *
from pyqt_worker import Worker
import utils.net_utils as net_utils
import utils.update_utils as update_utils
import platform
import qthreads.c_alive_report_thread
from g_defs.c_client import client
from g_defs.c_mediafileparam import mediafileparam
import utils.file_utils
import utils.log_utils
import utils.update_utils

import utils.ffmpy_utils
from g_defs.c_TreeWidgetItemSP import CTreeWidget

log = utils.log_utils.logging_init(__file__)

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(antialias=True)

        self.center()

        self.setWindowOpacity(0.9)  # 设置窗口透明度
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        #initial streaming ffmpy status
        self.ffmpy_running = play_status.stop
        self.play_type = play_type.play_none
        self.ff_process = None
        self.play_option_repeat = repeat_option.repeat_none

        self.setMouseTracking(True)
        self.init_ui()
        self.status = self.statusBar()
        self.status.showMessage("Main Page")

        self.setWindowTitle("LED Server")

        #get eth0 ip and set it to server_ip
        if platform.machine() in ('arm', 'arm64', 'aarch64'):
            ifname = 'eth0'
        else:
            ifname = 'enp8s0'
        self.server_ip = net_utils.get_ip_address(ifname)
        self.clients = []
        self.clients_mutex = QMutex()


        self.broadcast_thread = Worker(method=self.server_broadcast, data="ABCDE", port=server_broadcast_port)
        self.broadcast_thread.start()
        self.refresh_clients_thread = Worker(method=self.refresh_clients_list, sleep_time=5)
        self.refresh_clients_thread.start()

        self.client_alive_report_thread = qthreads.c_alive_report_thread.alive_report_thread(ip=self.server_ip, port=alive_report_port)
        self.client_alive_report_thread.check_client.connect(self.check_client)
        self.client_alive_report_thread.start()

        self.preview_file_name = ""


    def init_ui(self):
        self.setFixedSize(960, 700)

        pagelayout = QGridLayout()
        """Left UI Start"""
        top_left_frame = QFrame(self)
        top_left_frame.setFrameShape(QFrame.StyledPanel)
        # 　lef layout vertical
        button_layout = QVBoxLayout(top_left_frame)
        top_left_frame.setMouseTracking(True)

        btm_left_frame = QFrame(self)
        btm_left_frame.setMouseTracking(True)


        blank_label = QLabel(btm_left_frame)
        blank_label.setMouseTracking(True)
        blank_layout = QVBoxLayout(btm_left_frame)

        blank_label.setText("GIS LED")
        blank_label.setFixedHeight(200)
        blank_layout.addWidget(blank_label)

        # btn for connect client
        connect_btn = QPushButton(top_left_frame)
        connect_btn.setMouseTracking(True)
        #connect_btn.setStyleSheet('QPushButton {background-color: #A3C1DA; color: orange;}')
        connect_btn.setFixedSize(200, 30), connect_btn.setText("Connect Client")
        connect_btn.clicked.connect(self.fun_connect_clients)
        button_layout.addWidget(connect_btn)
        connect_btn.setMouseTracking(True)

        content_btn = QPushButton(top_left_frame)
        content_btn.setFixedSize(200, 30), content_btn.setText("Play Content")
        content_btn.clicked.connect(self.func_file_contents)
        button_layout.addWidget(content_btn)

        test_btn = QPushButton(top_left_frame)
        test_btn.setFixedSize(200, 30), test_btn.setText("TestA")
        test_btn.clicked.connect(self.func_testA)
        button_layout.addWidget(test_btn)

        test2_btn = QPushButton(top_left_frame)
        test2_btn.setFixedSize(200, 30), test2_btn.setText("TestB")
        test2_btn.clicked.connect(self.func_testB)
        button_layout.addWidget(test2_btn)
        """Left UI End"""

        """Right UI"""
        self.right_frame = QFrame(self)
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setMouseTracking(True)
        # 右边显示为stack布局
        self.right_layout = QStackedLayout(self.right_frame)

        """QTableWidget"""
        self.initial_client_table_page()

        """QTreeWidgetFile Tree in Tab.2"""
        self.initial_media_file_page()

        """QTreeWidget for LED Setting"""
        self.initial_led_layout_page()

        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.setMouseTracking(True)
        top_left_frame.setFixedHeight(250)
        top_left_frame.setFixedWidth(250)
        self.splitter1.addWidget(top_left_frame)
        self.splitter1.addWidget(btm_left_frame)

        self.splitter2 = QSplitter(Qt.Horizontal)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.setMouseTracking(True)
        # 　add right layout frame
        self.right_frame.setMouseTracking(True)
        self.splitter2.addWidget(self.right_frame)
        self.splitter2.setMouseTracking(True)
        # 窗口部件添加布局
        widget = QWidget()
        pagelayout.addWidget(self.splitter2)
        widget.setLayout(pagelayout)
        widget.setMouseTracking(True)
        self.setCentralWidget(widget)

        media_previre_widget = QLabel()
        media_previre_widget.setFrameShape(QFrame.StyledPanel)
        media_previre_widget.setWindowFlags(Qt.ToolTip)
        media_previre_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        media_previre_widget.hide()
        self.media_previre_widget = media_previre_widget

    def initial_client_table_page(self):

        """QTableWidget"""
        self.client_table = QTableWidget(self.right_frame)
        self.client_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.client_table.setColumnCount(3)
        self.client_table.setRowCount(0)

        self.client_table.setMouseTracking(True)
        self.client_table.setHorizontalHeaderLabels(['IP', 'ID', 'Status'])
        self.client_table.setColumnWidth(0, 200) #IP Column width:200
        client_widget = QWidget(self.right_frame)
        client_layout = QVBoxLayout()
        client_widget.setLayout(client_layout)
        client_layout.addWidget(self.client_table)
        #right click menu
        self.client_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.client_table.customContextMenuRequested.connect(self.clientsmenuContextTree)
        self.right_layout.addWidget(client_widget)



    def initial_media_file_page(self):
        # QTreeWidgetFile Tree in Tab.2
        self.file_tree = CTreeWidget(self.right_frame)
        self.file_tree.mouseMove.connect(self.cmouseMove)
        self.file_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_tree.setColumnCount(1)
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.headerItem().setText(0, "Media Files")
        font = QFont()
        font.setPointSize(24)
        self.file_tree.setFont(font)

        # Add Internal Media Folder in tree root
        self.internal_media_root = QTreeWidgetItem(self.file_tree)

        self.internal_media_root.setText(0, "Internal Media")
        self.internal_files_list = utils.file_utils.get_media_file_list(internal_media_folder)
        log.debug("file_list = %s", self.internal_files_list)
        for f in self.internal_files_list:
            internal_file_item = QTreeWidgetItem()
            internal_file_item.setText(0, os.path.basename(f))
            utils.ffmpy_utils.gen_webp_from_video(internal_media_folder, os.path.basename(f))
            self.internal_media_root.addChild(internal_file_item)

        self.file_tree.addTopLevelItem(self.internal_media_root)
        self.file_tree.parentWidget().setMouseTracking(True)
        self.file_tree.setMouseTracking(True)

        # Add External Media Folder in tree root
        self.external_media_root_list = []
        for mount_point in utils.file_utils.get_mount_points():
            external_media_root = QTreeWidgetItem(self.file_tree)
            external_media_root.setText(0, "External Media" + ":" + mount_point)
            self.external_files_list = utils.file_utils.get_media_file_list(mount_point)
            log.debug("file_list = %s", self.external_files_list)
            for f in self.external_files_list:
                external_file_item = QTreeWidgetItem()
                external_file_item.setText(0, os.path.basename(f))
                utils.ffmpy_utils.gen_webp_from_video(mount_point, os.path.basename(f))
                external_media_root.addChild(external_file_item)
            self.external_media_root_list.append(external_media_root)
            self.file_tree.addTopLevelItem(external_media_root)

        # playlist file tree
        self.media_play_list = []
        self.load_playlist()
        self.qtw_media_play_list = QTreeWidgetItem(self.file_tree)
        self.qtw_media_play_list.setText(0, "Playlist")
        self.file_tree.addTopLevelItem(self.qtw_media_play_list)
        self.file_tree.expandAll()
        """self.file_tree.itemClicked.connect(self.onFileTreeItemClicked)
        self.file_tree.itemEntered.connect(self.itemEntered)
        self.file_tree.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.file_tree.itemChanged.connect(self.itemChanged)
        self.file_tree.viewportEntered.connect(self.file_tree_viewportEntered)"""
        self.file_tree.setMouseTracking(True)
        # Add right clicked function signal/slot
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.menuContextTree)

        log.debug("mount point : %s", utils.file_utils.get_mount_points())
        # log.debug("%s", self.file_tree.indexOfTopLevelItem(internal_media_root))
        # log.debug("%s", self.file_tree.itemAt( 0, 1).text(0))

        """play singal file btn"""
        self.btn_play_select_file = QPushButton(self.right_frame)
        self.btn_play_select_file.setText("Play Select File")
        self.btn_play_select_file.setFixedWidth(110)
        self.btn_play_select_file.setDisabled(True)

        """play playlist btn"""
        self.btn_play_playlist = QPushButton(self.right_frame)
        self.btn_play_playlist.setText("Play Playlist")
        self.btn_play_playlist.setFixedWidth(110)
        if len(self.media_play_list) == 0:
            self.btn_play_playlist.setDisabled(True)
        self.btn_play_playlist.clicked.connect(self.play_playlist_trigger)

        """stop btn"""
        self.btn_stop = QPushButton(self.right_frame)
        self.btn_stop.setText("Stop")
        self.btn_stop.setFixedWidth(110)
        self.btn_stop.clicked.connect(self.stop_media_trigger)

        self.btn_pause = QPushButton(self.right_frame)
        self.btn_pause.setText("Pause")
        self.btn_pause.setFixedWidth(110)
        self.btn_pause.clicked.connect(self.pause_media_trigger)

        self.btn_repeat = QPushButton(self.right_frame)
        if self.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")

        self.btn_repeat.setFixedWidth(110)
        self.btn_repeat.clicked.connect(self.repeat_option_trigger)

        self.play_option_widget = QWidget(self.right_frame)
        play_option_layout = QHBoxLayout()
        self.play_option_widget.setLayout(play_option_layout)
        play_option_layout.addWidget(self.btn_play_select_file)
        play_option_layout.addWidget(self.btn_play_playlist)
        play_option_layout.addWidget(self.btn_stop)
        play_option_layout.addWidget(self.btn_pause)
        play_option_layout.addWidget(self.btn_repeat)

        self.play_option_widget.setMouseTracking(True)

        self.file_tree_widget = QWidget(self.right_frame)
        file_tree_layout = QVBoxLayout()
        self.file_tree_widget.setLayout(file_tree_layout)
        file_tree_layout.addWidget(self.file_tree)
        file_tree_layout.addWidget(self.play_option_widget)
        self.file_tree_widget.setMouseTracking(True)
        # file_tree_layout.addWidget(self.btn_play)
        # file_tree_layout.addWidget(self.btn_stop)
        self.right_layout.addWidget(self.file_tree_widget)

    def initial_led_layout_page(self):
        self.led_setting_cabnet = QWidget(self.right_frame)
        self.led_setting = QWidget(self.right_frame)
        led_setting_layout = QVBoxLayout()
        self.led_setting.setLayout(led_setting_layout)
        led_setting_layout.addWidget(self.led_setting_cabnet)
        self.right_layout.addWidget(self.led_setting)


    def center(self):
        '''
        get the geomertry of the screen and set the postion in the center of screen
        '''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def fun_connect_clients(self):
        log.debug("connect clients")

        self.right_layout.setCurrentIndex(0)

    def func_file_contents(self):
        log.debug("file contents")

        self.right_layout.setCurrentIndex(1)

    def func_testA(self):
        log.debug("testA")
        self.right_layout.setCurrentIndex(2)
        """file = QFileDialog().getOpenFileName()
        log.debug("file_uri:", file[0])
        update_utils.upload_client_image(file[0])"""

    def func_testB(self):
        log.debug("testB")
        self.media_previre_widget.show()

        ips = []
        ips.append("192.168.0.52")
        utils.update_utils.upload_update_swu_to_client(ips,
                                                       "/media/venom/XXX/sandbox/ledclient_updates_folder/rpi-ledclient_20210810_001.swu",
                                                       update_utils.request_ret())
        self.right_layout.setCurrentIndex(3)

    """ handle the command from qlocalserver"""
    def parser_cmd_from_qlocalserver(self, data):
        log.debug("data : ", data)

    def check_client(self, ip):
        #log.debug("Enter function check_client, ip: %s", ip)
        is_found = False
        tmp_client = None
        try:
            self.clients_lock()
            for c in self.clients:
                if c.client_ip == ip:
                    is_found = True
                    tmp_client = c
                    break
            """ no such client ip in clients list, new one and append"""
            if is_found is False:
                c = client(ip)
                self.clients.append(c)
                self.refresh_client_table()
            else:
                """ find this ip in clients list, set the alive report count"""
                tmp_client.set_alive_count(5)
        except Exception as e:
            log.debug(e)
        finally:
            self.clients_unlock()
        """for c in self.clients:
            log.debug("client.ip : %s", c.client_ip)
            log.debug("client.alive_val : %s", c.alive_val)"""


    """send broadcast on eth0"""
    def server_broadcast(self, arg):
        data = arg.get("data")
        port = arg.get("port")

        #print("platform.machine :", platform.machine())
        if platform.machine() in ('arm', 'arm64', 'aarch64'):
            ifname = 'eth0'
        else:
            ifname = 'enp8s0'
        ip = net_utils.get_ip_address(ifname)
        #print("ip : ", ip)
        msg = data.encode()
        if ip != "":
            #print(f'sending on {ip}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((ip, 0))
            sock.sendto(msg, ("255.255.255.255", port))
            sock.close()

        sleep(2)
    

    def clients_lock(self):
        self.clients_mutex.lock()

    def clients_unlock(self):
        self.clients_mutex.unlock()

    def refresh_clients_list(self, arg):
        #is_list_changed = False
        ori_len = len(self.clients)
        try:
            self.clients_lock()
            ori_len = len(self.clients)
            sleep_time = arg.get("sleep_time")
            for c in self.clients:
                c.decrese_alive_count()
                if c.get_alive_count() == 0:
                    self.clients.remove(c)

            """for c in self.clients:
                log.debug("c.client_ip : %s ", c.client_ip)"""
        except Exception as e:
            log.debug(e)
        finally:
            if ori_len != len(self.clients):
                self.refresh_client_table()
            self.clients_unlock()

        sleep(sleep_time)


    def refresh_client_table(self):
        row_count = self.client_table.rowCount()
        for i in range(row_count):
            row_to_remove = self.client_table.rowAt(i)
            self.client_table.removeRow(row_to_remove)

        for c in self.clients:
            row_count = self.client_table.rowCount()
            self.client_table.insertRow(row_count)
            self.client_table.setItem(row_count, 0, QTableWidgetItem(c.client_ip))

    @pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onFileTreeItemClicked(self, it, col):
        log.debug("%s, %s, %s", it, col, it.text(col))
        if it.parent() is not None:
            log.debug("%s", it.parent().text(0))
            # play the file
            if it.parent().text(0) == 'Internal Media':
                file_uri = internal_media_folder + "/" +it.text(col)
            else:
                if 'External Media' in it.parent().text(0):
                    dir = it.parent().text(0).split(":")[1]
                    file_uri = dir + "/" + it.text(col)

            log.debug("%s", file_uri)

    #client table right clicked slot function
    def clientsmenuContextTree(self, position):
        QTableWidgetItem = self.client_table.itemAt(position)
        if QTableWidgetItem is None:
            return
        log.debug("client ip :%s", QTableWidgetItem.text())
        self.right_click_select_client_ip = QTableWidgetItem.text()

        popMenu = QMenu()
        playAct = QAction("fw upgrade", self)
        popMenu.addAction(playAct)
        popMenu.addSeparator()
        addtoplaylistAct = QAction("Test", self)
        popMenu.addAction(addtoplaylistAct)
        popMenu.triggered[QAction].connect(self.popmenu_trigger_act)

        popMenu.exec_(self.client_table.mapToGlobal(position))

    #right clicked slot function
    def menuContextTree(self, position):
        widgetitem = self.file_tree.itemAt(position)
        log.debug("%s", widgetitem.text(0))
        if widgetitem.parent() is not None:
            log.debug("client")
            if widgetitem.parent().text(0) == "Internal Media":
                self.right_clicked_select_file_uri = internal_media_folder + "/" + widgetitem.text(0)
            elif widgetitem.parent().text(0) == "External Media":
                self.right_clicked_select_file_uri = widgetitem.parent().text(0).split(":")[1] + "/" + widgetitem.text()
            elif widgetitem.parent().text(0) == "Playlist":
                log.debug("no playlist right click")
                return
        else:
            log.debug("root")
            return
        #self.right_click_select_file =
        popMenu = QMenu()
        playAct = QAction("Play", self)
        popMenu.addAction(playAct)
        popMenu.addSeparator()
        addtoplaylistAct = QAction("AddtoPlaylist", self)
        popMenu.addAction(addtoplaylistAct)
        popMenu.triggered[QAction].connect(self.popmenu_trigger_act)

        popMenu.exec_(self.file_tree.mapToGlobal(position))

    def popmenu_trigger_act(self, q):
        log.debug("%s", q.text())
        if q.text() == "Play":
            """play single file"""
            self.ff_process = utils.ffmpy_utils.ffmpy_execute(self, self.right_clicked_select_file_uri)
            self.play_type = play_type.play_single
        elif q.text() == "AddtoPlaylist":
            """Add this file_path to playlist"""
            """UI first"""
            fileuri_treewidget = QTreeWidgetItem()
            log.debug("fileuri : %s", self.right_clicked_select_file_uri.rsplit("/", 1)[1])
            fileuri_treewidget.setText(0, self.right_clicked_select_file_uri.rsplit("/", 1)[1])
            self.qtw_media_play_list.addChild(fileuri_treewidget)

            """refresh media_play_list """
            mediafile = mediafileparam(self.right_clicked_select_file_uri)
            self.media_play_list.append(mediafile)
            log.debug("Add file uri to playlist")
            if len(self.media_play_list) > 0:
                self.btn_play_playlist.setDisabled(False)
        elif q.text() == "fw upgrade":
            log.debug("fw upgrade")
            #upgrade_file_uri, upgrade_file_type = QFileDialog.getOpenFileUrl(self,"Select Upgrade File", "/home/root/", "SWU File (*.swu)" )
            #upgrade_file_uri, upgrade_file_type = QFileDialog.getOpenFileUrl(None,"Select Upgrade File", "/home/root/", "All Files (*);;")
            upgrade_file_uri = QFileDialog.getOpenFileName(None,"Select Upgrade File", "/home/root/")

            if upgrade_file_uri == "":
                log.debug("No select")
                return
            log.debug("upgrade_file_uri = %s", upgrade_file_uri[0])
            if upgrade_file_uri[0].endswith("swu"):
                log.debug("Goto upgrade!")
                utils.upload_utils.upload_upgrade_image(self.right_click_select_client_ip, upgrade_file_uri[0])
            else:
                return


    def load_playlist(self):
        log.error("not Implement yet")

    def play_playlist_trigger(self):
        log.debug("")
        self.play_type = play_type.play_playlist
        thread_1 = threading.Thread(target=utils.ffmpy_utils.ffmpy_execute_list, args=(self, self.media_play_list,))
        thread_1.start()
        #utils.ffmpy_utils.ffmpy_execute_list(self, self.media_play_list)

    def stop_media_trigger(self):
        log.debug("")
        """if playtype is play file_list, stop it first"""
        if self.play_type == play_type.play_playlist:
            self.play_type = play_type.play_none

        """check the popen subprocess is alive or not"""
        if self.ff_process.poll() is None:
            log.debug("send sigterm!")
            os.kill(self.ff_process.pid, signal.SIGTERM)
            self.ffmpy_running = play_status.stop
        
        if len(self.media_play_list) > 0:
            self.btn_play_playlist.setDisabled(False)

    def pause_media_trigger(self):
        """check the popen subprocess is alive or not"""
        if self.ff_process is None:
            log.debug("No ff_process")
            return
        if self.ff_process.poll() is None:
            log.debug("self.ff_process is alive")
            if self.ffmpy_running == play_status.playing:
                log.debug("send sigstop for pause!")
                os.kill(self.ff_process.pid, signal.SIGSTOP)
                self.ffmpy_running = play_status.pausing
                self.btn_pause.setText("Resume")
            elif self.ffmpy_running == play_status.pausing:
                log.debug("send sigcont for playing!")
                os.kill(self.ff_process.pid, signal.SIGCONT)
                self.ffmpy_running = play_status.playing
                self.btn_pause.setText("Pause")
        else:
            log.debug("self.ff_process is Not alive")

    def repeat_option_trigger(self):
        if self.play_option_repeat >= repeat_option.repeat_option_max:
            self.play_option_repeat = repeat_option.repeat_none
        else:
            self.play_option_repeat += 1

        if self.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")
        log.debug("self.play_option_repeat : %d", self.play_option_repeat)

    def mouseMoveEvent(self, event):
        #log.debug("mouseMoveEvent")
        if self.media_previre_widget.isVisible() is True:
            self.media_previre_widget.hide()
            self.preview_file_name = ""

    """def itemEntered(self ):
        log.debug("itemEntered")

    def itemSelectionChanged(self):
        log.debug("itemSelectionChanged")

    def itemChanged(self):
        log.debug("itemChanged")

    def file_tree_viewportEntered(self):
        log.debug("file_tree_viewportEntered")"""

    def cmouseMove(self, event):
        #log.debug("cmouseMove")
        
        #log.debug("%s", QMovie.supportedFormats())
        if self.file_tree.itemAt(event.x(), event.y()) is None:
            if self.media_previre_widget.isVisible() is True:
                self.media_previre_widget.hide()
            return
        #log.debug("cmouseMove %s", self.file_tree.itemAt(event.x(), event.y()).text(0))
        if self.file_tree.itemAt(event.x(), event.y()).text(0) in  ["Internal Media", "External Media:", "Playlist"]:
            log.debug("None treewidgetitem")
            if self.media_previre_widget.isVisible() is True:
                self.media_previre_widget.hide()
                self.preview_file_name = ""
        else:
            if self.file_tree.itemAt(event.x(), event.y()).text(0) == self.preview_file_name:
                log.debug("The same movie")
                log.debug("%s", self.preview_file_name)
            else:
                self.media_previre_widget.setGeometry(self.file_tree.x() + event.x(), self.file_tree.y() + event.y(), 640, 480)
                self.preview_file_name = self.file_tree.itemAt(event.x(), event.y()).text(0)
                self.movie = QMovie(internal_media_folder + ThumbnailFileFolder + self.preview_file_name.replace(".mp4", ".webp"))
                self.media_previre_widget.setMovie(self.movie)
                self.movie.start()
                self.media_previre_widget.show()


