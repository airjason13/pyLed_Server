import platform
import os
import signal
import threading
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
                            QGridLayout, QFrame,QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                            QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
                             QFileDialog, QListWidget, QFileSystemModel, QTreeView, QMenu, QAction, QAbstractItemView)
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QMovie, QPixmap, QPainter
from PyQt5.QtCore import Qt, QMutex, pyqtSlot, QModelIndex, pyqtSignal
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
import utils.qtui_utils
from random import *
import utils.ffmpy_utils
from c_led_layout_window import LedLayoutWindow
from c_cabinet_setting_window import CabinetSettingWindow
from g_defs.c_TreeWidgetItemSP import CTreeWidget
from g_defs.c_cabinet_params import cabinet_params
from commands_def import *
log = utils.log_utils.logging_init(__file__)

class MainUi(QMainWindow):
    signal_add_cabinet_label = pyqtSignal(cabinet_params)
    signal_redraw_cabinet_label = pyqtSignal(cabinet_params, Qt.GlobalColor)
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(antialias=True)

        self.center()
        self.setWindowOpacity(1.0)  # 设置窗口透明度
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        ''' Set Led layout params'''
        self.led_wall_width = default_led_wall_width
        self.led_wall_height = default_led_wall_height
        self.led_cabinet_width = default_led_cabinet_width
        self.led_cabinet_height = default_led_cabinet_height

        self.led_layout_window = LedLayoutWindow(self.led_wall_width, self.led_wall_height,
                                                 self.led_cabinet_width, self.led_cabinet_height,
                                                 default_led_wall_margin)
        self.signal_add_cabinet_label.connect(self.led_layout_window.add_cabinet_label)
        self.signal_redraw_cabinet_label.connect(self.led_layout_window.redraw_cabinet_label)

        self.cabinet_setting_window = CabinetSettingWindow(None)
        self.cabinet_setting_window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.cabinet_setting_window.signal_set_cabinet_params.connect(self.set_cabinet_params)
        self.cabinet_setting_window.signal_draw_temp_cabinet.connect(self.draw_cabinet_label)
        self.cabinet_setting_window.signal_set_default_cabinet_resolution.connect(self.set_default_cabinet_resolution)
        self.client_led_layout = []

        '''main ui right frame page index'''
        self.page_idx = 0

        #initial streaming ffmpy status
        self.ffmpy_running = play_status.stop
        self.play_type = play_type.play_none
        self.ff_process = None
        self.play_option_repeat = repeat_option.repeat_none

        self.setMouseTracking(True)
        self.init_ui()
        self.page_status = self.statusBar()
        self.page_status.showMessage("Client Page")

        self.setWindowTitle("LED Server")

        #get eth0 ip and set it to server_ip
        self.server_ip = net_utils.get_ip_address()
        self.clients = []
        self.clients_mutex = QMutex()
        ''' for check cmd seq '''
        self.cmd_send_seq_id = 0
        self.cmd_seq_id_mutex = QMutex()

        self.client_id_count = 0


        self.broadcast_thread = Worker(method=self.server_broadcast, data=server_broadcast_message, port=server_broadcast_port)
        self.broadcast_thread.start()
        self.refresh_clients_thread = Worker(method=self.refresh_clients_list, sleep_time=5)
        self.refresh_clients_thread.start()

        self.client_alive_report_thread = qthreads.c_alive_report_thread.alive_report_thread(ip=self.server_ip, port=alive_report_port)
        self.client_alive_report_thread.check_client.connect(self.check_client)
        self.client_alive_report_thread.start()

        self.preview_file_name = ""

        self.send_cmd_fail_msg = QMessageBox()



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


        version_label = QLabel(btm_left_frame)
        version_label.setMouseTracking(True)
        blank_layout = QVBoxLayout(btm_left_frame)

        version_label.setText("GIS LED\n" + "version:" + version)
        version_label.setFixedHeight(200)

        test_label = QLabel(btm_left_frame)
        test_pixmap = utils.qtui_utils.gen_led_layout_type_pixmap(200, 100, 10, 1)
        test_label.setPixmap(test_pixmap)
        blank_layout.addWidget(test_label)

        blank_layout.addWidget(version_label)

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
        test_btn.setFixedSize(200, 30), test_btn.setText("LED Setting")
        test_btn.clicked.connect(self.func_led_setting)
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

        media_preview_widget = QLabel()
        media_preview_widget.setFrameShape(QFrame.StyledPanel)
        media_preview_widget.setWindowFlags(Qt.ToolTip)
        media_preview_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        media_preview_widget.hide()
        self.media_preview_widget = media_preview_widget

    def initial_client_table_page(self):

        """QTableWidget"""
        self.client_table = QTableWidget(self.right_frame)
        self.client_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        ''' ip, id, status, version'''
        self.client_table.setColumnCount(4)
        self.client_table.setRowCount(0)

        self.client_table.setMouseTracking(True)
        self.client_table.setHorizontalHeaderLabels(['IP', 'ID', 'Status', 'Version'])
        self.client_table.setColumnWidth(0, 200) #IP Column width:200
        self.client_table.setColumnWidth(3, 200)  # Version Column width:200
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
        self.file_tree.mouseMove.connect(self.media_page_mouseMove)

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

        self.file_tree.setMouseTracking(True)
        # Add right clicked function signal/slot
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.menuContextTree)

        log.debug("mount point : %s", utils.file_utils.get_mount_points())

        """play singal file btn"""
        self.btn_play_select_file = QPushButton(self.right_frame)
        self.btn_play_select_file.setText("Play Select File")
        self.btn_play_select_file.setFixedWidth(media_btn_width)
        self.btn_play_select_file.setDisabled(True)

        """play playlist btn"""
        self.btn_play_playlist = QPushButton(self.right_frame)
        self.btn_play_playlist.setText("Play Playlist")
        self.btn_play_playlist.setFixedWidth(media_btn_width)
        if len(self.media_play_list) == 0:
            self.btn_play_playlist.setDisabled(True)
        self.btn_play_playlist.clicked.connect(self.play_playlist_trigger)

        """stop btn"""
        self.btn_stop = QPushButton(self.right_frame)
        self.btn_stop.setText("Stop")
        self.btn_stop.setFixedWidth(media_btn_width)
        self.btn_stop.clicked.connect(self.stop_media_trigger)

        self.btn_pause = QPushButton(self.right_frame)
        self.btn_pause.setText("Pause")
        self.btn_pause.setFixedWidth(media_btn_width)
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

        self.btn_repeat.setFixedWidth(media_btn_width)
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
        self.led_setting = QWidget(self.right_frame)

        ''' led setting options'''
        self.led_setting_width_textlabel = QLabel(self.right_frame)
        self.led_setting_width_textlabel.setText('LED Wall Width:')
        self.led_setting_width_editbox = QLineEdit(self.right_frame)
        self.led_setting_width_editbox.setFixedWidth(120)
        self.led_setting_width_editbox.setText(str(self.led_wall_width))
        self.led_setting_height_textlabel = QLabel(self.right_frame)
        self.led_setting_height_textlabel.setText('LED Wall Height:')
        self.led_setting_height_editbox = QLineEdit(self.right_frame)
        self.led_setting_height_editbox.setFixedWidth(120)
        self.led_setting_height_editbox.setText(str(self.led_wall_height))
        self.led_res_check_btn = QPushButton()
        self.led_res_check_btn.clicked.connect(self.set_led_wall_size)
        self.led_res_check_btn.setText("Confirm")


        self.led_setting_layout = QGridLayout()

        self.led_setting_layout.addWidget(self.led_setting_width_textlabel, 0, 1)
        self.led_setting_layout.addWidget(self.led_setting_width_editbox, 0, 2)
        self.led_setting_layout.addWidget(self.led_setting_height_textlabel, 0, 3)
        self.led_setting_layout.addWidget(self.led_setting_height_editbox, 0, 4)
        self.led_setting_layout.addWidget(self.led_res_check_btn, 0, 5)

        self.led_setting.setLayout(self.led_setting_layout)


        #self.led_setting_layout.addWidget(self.led_fake_label, 1, 0, 1, 5)
        self.led_client_layout_tree = CTreeWidget(self.right_frame)
        self.led_client_layout_tree.mouseMove.connect(self.led_client_layout_mouse_move)
        self.led_client_layout_tree.setMouseTracking(True)
        self.led_client_layout_tree.setSelectionMode(QAbstractItemView.MultiSelection)

        self.led_client_layout_tree.doubleClicked.connect(self.cabinet_setting_window_show)

        self.led_client_layout_tree.setColumnCount(1)
        self.led_client_layout_tree.setColumnWidth(0, 300)
        self.led_client_layout_tree.headerItem().setText(0, "Client Layout")


        font = QFont()
        font.setPointSize(24)
        self.led_client_layout_tree.setFont(font)


        self.led_setting_layout.addWidget(self.led_client_layout_tree, 1, 0, 1, 6)

        self.led_setting_layout.setRowStretch(1, 1)
        self.right_layout.addWidget(self.led_setting)

        port_layout_infomation_widget = QLabel()
        port_layout_infomation_widget.setFrameShape(QFrame.StyledPanel)
        port_layout_infomation_widget.setWindowFlags(Qt.ToolTip)
        port_layout_infomation_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        port_layout_infomation_widget.hide()
        self.port_layout_infomation_widget = port_layout_infomation_widget

    def center(self):
        '''
        get the geomertry of the screen and set the postion in the center of screen
        '''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def fun_connect_clients(self):
        log.debug("connect clients")
        self.page_idx = 0
        self.right_layout.setCurrentIndex(self.page_idx)
        self.page_status_change()

    def func_file_contents(self):
        log.debug("file contents")
        self.page_idx = 1
        self.right_layout.setCurrentIndex(self.page_idx)
        self.page_status_change()

    def func_led_setting(self):
        log.debug("func_led_setting")
        self.page_idx = 2
        self.right_layout.setCurrentIndex(self.page_idx)
        self.page_status_change()
        self.led_layout_window.show()
        """file = QFileDialog().getOpenFileName()
        log.debug("file_uri:", file[0])
        update_utils.upload_client_image(file[0])"""

    def func_testB(self):
        log.debug("testB")
        self.media_preview_widget.show()
        self.test_cmd_thread = Worker(method=self.cmd_test, )
        self.test_cmd_thread.start()

        self.right_layout.setCurrentIndex(3)

    """ handle the command from qlocalserver"""
    def parser_cmd_from_qlocalserver(self, data):
        log.debug("data : ", data)

    def check_client(self, ip, data):
        #log.debug("Enter function check_client, ip: %s", ip)
        #log.debug("%s", data)
        is_found = False
        tmp_client = None
        c_version = ""
        try:
            c_version = data.split(";")[1].split(":")[1]
            self.clients_lock()
            for c in self.clients:
                if c.client_ip == ip:
                    is_found = True
                    tmp_client = c
                    break
            """ no such client ip in clients list, new one and append"""
            if is_found is False:
                c = client(ip, net_utils.get_ip_address(), c_version, self.client_id_count)
                #connect signal/slot function
                c.signal_send_cmd_ret.connect(self.client_send_cmd_ret)
                c.signal_cabinet_params_changed.connect(self.send_cmd_set_cabinet_params)

                self.client_id_count += 1
                self.clients.append(c)

                self.sync_client_cabinet_params(c.client_ip, False)

                self.refresh_client_table()
            else:
                """ find this ip in clients list, set the alive report count"""
                tmp_client.set_alive_count(5)
        except Exception as e:
            log.debug(e)
        finally:
            self.clients_unlock()




    """send broadcast on eth0"""
    def server_broadcast(self, arg):
        data = arg.get("data")
        port = arg.get("port")

        ip = net_utils.get_ip_address()
        utils.net_utils.force_set_eth_ip()

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

        ''' led layout page treewidget show'''
        #log.debug("self.led_client_layout_tree.topLevelItemCount() = %d",self.led_client_layout_tree.topLevelItemCount())
        #log.debug("len(self.clients) = %d", len(self.clients))
        if self.led_client_layout_tree.topLevelItemCount() != len(self.clients):
            self.client_led_layout.clear()
            self.led_client_layout_tree.clear()

            for c in self.clients:
                client_led_layout = QTreeWidgetItem(self.led_client_layout_tree)
                client_led_layout.setText(0, "id:" + str(c.client_id) + "(ip:" + c.client_ip + ")")
                for i in range(8):
                    port_layout = QTreeWidgetItem(client_led_layout)
                    port_layout.setText(0, "port" + str(i) + ":")

                    '''cabinet params test start '''
                    test_params = QTreeWidgetItem(port_layout)
                    test_params.setText(0, 'test')
                    '''cabinet params test end '''

                    #gen cabinet label in led_wall_layout_window
                    self.signal_add_cabinet_label.emit(c.cabinets_setting[i])

                self.client_led_layout.append(client_led_layout)



    def refresh_client_table(self):
        row_count = self.client_table.rowCount()
        for i in range(row_count):
            row_to_remove = self.client_table.rowAt(i)
            self.client_table.removeRow(row_to_remove)

        for c in self.clients:
            row_count = self.client_table.rowCount()
            self.client_table.insertRow(row_count)
            self.client_table.setItem(row_count, 0, QTableWidgetItem(c.client_ip))
            self.client_table.setItem(row_count, 1, QTableWidgetItem(str(c.client_id)))
            self.client_table.setItem(row_count, 3, QTableWidgetItem(c.client_version))




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

        popMenu.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + \
                              """
                              QMenu{
                                  button-layout : 2;
                                  font: bold 16pt "Brutal Type";
                                  border: 3px solid #FFA042;
                                  border-radius: 8px;
                                  }
                              """)
        fw_upgrade_Act = QAction("fw upgrade", self)
        popMenu.addAction(fw_upgrade_Act)
        popMenu.addSeparator()
        test_Act = QAction("test", self)
        popMenu.addAction(test_Act)
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

        popMenu.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + \
                    """
                    QMenu{
                        button-layout : 2;
                        font: bold 16pt "Brutal Type";
                        border: 3px solid #FFA042;
                        border-radius: 8px;
                        }
                    """)

        playAct = QAction("Play", self)
        popMenu.addAction(playAct)
        popMenu.addSeparator()
        addtoplaylistAct = QAction("AddtoPlaylist", self)
        popMenu.addAction(addtoplaylistAct)
        popMenu.triggered[QAction].connect(self.popmenu_trigger_act)

        popMenu.exec_(self.file_tree.mapToGlobal(position))

    """All popmenu trigger act"""
    def popmenu_trigger_act(self, q):
        log.debug("%s", q.text())
        if q.text() == "Play":
            """play single file"""
            self.ff_process = utils.ffmpy_utils.ffmpy_execute(self, self.right_clicked_select_file_uri, width=160, height=96)
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
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                upgrade_file_uri = QFileDialog.getOpenFileName(None, "Select Upgrade File", "/home/root/")
            else:
                upgrade_file_uri = QFileDialog.getOpenFileName(None, "Select Upgrade File", "/home/venom/","SWU File (*.swu)")

            if upgrade_file_uri == "":
                log.debug("No select")
                return
            log.debug("upgrade_file_uri = %s", upgrade_file_uri[0])
            if upgrade_file_uri[0].endswith("swu"):
                log.debug("Goto upgrade!")
                ips = []
                ips.append(self.right_click_select_client_ip)
                utils.update_utils.upload_update_swu_to_client(ips, upgrade_file_uri[0], utils.update_utils.update_client_callback)
            else:
                return
        elif q.text() == "test":
            for c in self.clients:
                if c.client_ip == self.right_click_select_client_ip:
                    log.debug("ready to send command")
                    cmd = "get_version"
                    param = "get_version"
                    c.send_cmd( cmd=cmd, cmd_seq_id=self.cmd_seq_id_increase(), param=param)


    def load_playlist(self):
        log.error("not Implement yet")

    def play_playlist_trigger(self):
        log.debug("")
        self.play_type = play_type.play_playlist
        thread_1 = threading.Thread(target=utils.ffmpy_utils.ffmpy_execute_list, args=(self, self.media_play_list, ))
        thread_1.start()


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
        if self.media_preview_widget.isVisible() is True:
            self.media_preview_widget.hide()
            self.preview_file_name = ""
        if self.port_layout_infomation_widget.isVisible() is True:
            self.port_layout_infomation_widget.hide()

    '''media page mouse move slot'''
    def led_client_layout_mouse_move(self, event):
        if self.led_client_layout_tree.itemAt(event.x(), event.y()) is None:
            if self.port_layout_infomation_widget.isVisible() is True:
                self.port_layout_infomation_widget.hide()
            return
        if self.led_client_layout_tree.itemAt(event.x(), event.y()).text(0).startswith("id"):
            if self.port_layout_infomation_widget.isVisible() is True:
                self.port_layout_infomation_widget.hide()
        else:

            self.port_layout_infomation_widget.setText("port layout :\n" +
                                                       "width :\n" +
                                                       "height :\n" +
                                                       "layout_type :\n" +
                                                       "start_point :\n"
                                                       )
            self.port_layout_infomation_widget.setGeometry(self.x() + self.right_frame.x() + self.led_client_layout_tree.x() + event.x() + 200,
                                                           self.y() + self.right_frame.y() + self.led_client_layout_tree.y() + event.y() + 100,
                                                           320, 240)
            self.port_layout_infomation_widget.show()



    '''media page mouse move slot'''
    def media_page_mouseMove(self, event):
        #log.debug("media_page_mouseMove")
        
        #log.debug("%s", QMovie.supportedFormats())
        if self.file_tree.itemAt(event.x(), event.y()) is None:
            if self.media_preview_widget.isVisible() is True:
                self.media_preview_widget.hide()
            return
        #log.debug("media_page_mouseMove %s", self.file_tree.itemAt(event.x(), event.y()).text(0))
        if self.file_tree.itemAt(event.x(), event.y()).text(0) in ["Internal Media", "External Media:", "Playlist"]:
            #log.debug("None treewidgetitem")
            if self.media_preview_widget.isVisible() is True:
                self.media_preview_widget.hide()
                self.preview_file_name = ""
        else:
            if self.file_tree.itemAt(event.x(), event.y()).text(0) == self.preview_file_name:
                #log.debug("The same movie")
                #log.debug("%s", self.preview_file_name)
                pass
            else:
                self.media_preview_widget.setGeometry(self.file_tree.x() + event.x(), self.file_tree.y() + event.y(), 640, 480)
                self.preview_file_name = self.file_tree.itemAt(event.x(), event.y()).text(0)
                self.movie = QMovie(internal_media_folder + ThumbnailFileFolder + self.preview_file_name.replace(".mp4", ".webp"))
                self.media_preview_widget.setMovie(self.movie)
                self.movie.start()
                self.media_preview_widget.show()


    def cmd_seq_id_lock(self):
        self.cmd_seq_id_mutex.lock()

    def cmd_seq_id_unlock(self):
        self.cmd_seq_id_mutex.unlock()

    ''' cmd seqid increase method
        cmd seqid range : 0~65534'''
    def cmd_seq_id_increase(self):
        self.cmd_seq_id_lock()
        self.cmd_send_seq_id += 1
        if self.cmd_send_seq_id >= 65535:
            self.cmd_send_seq_id = 0
        self.cmd_seq_id_unlock()
        log.debug("self.cmd_send_seq_id :%d", self.cmd_send_seq_id)
        return self.cmd_send_seq_id

    def cmd_reply_callback(self,  ret, recvData=None, client_ip=None, client_reply_port=None):
        log.debug("ret :%s", ret)


    """Just for Test random command trigger"""
    def cmd_test(self, arg):
        while True:

            for c in self.clients:
                for i in range(4):
                    if i == 4:
                        cmd = "spec_test"
                    elif i == 3:
                        cmd = "set_cabinet_size"
                    elif i == 2:
                        cmd = "set_led_size"
                    elif i == 1:
                        cmd = "get_pico_num"
                    elif i == 0:
                        cmd = "get_version"
                    param = "abcde"
                    c.send_cmd(cmd=cmd, cmd_seq_id=self.cmd_seq_id_increase(), param=param)
                    time.sleep(0.1)

    def client_send_cmd_ret(self, ret, send_cmd, recvData=None, client_ip=None, client_reply_port=None):
        if ret is False:
            log.fatal("client_ip : %s", client_ip)
            #self.send_cmd_fail_msg.hide()
            if self.send_cmd_fail_msg is not None:
                try:
                    self.send_cmd_fail_msg.setIcon(QMessageBox.Critical)
                    self.send_cmd_fail_msg.setText("Error")
                    self.send_cmd_fail_msg.setInformativeText("Can not get response of " + send_cmd + " from " + client_ip)
                    self.send_cmd_fail_msg.setWindowTitle("Error")
                    self.send_cmd_fail_msg.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                    self.send_cmd_fail_msg.show()
                except Exception as e:
                    log.fatal(e)
        else:
            if send_cmd.startswith("get") :
                if client_ip is not None:
                    for c in self.clients:
                        if c.client_ip == client_ip:
                            c.parse_get_cmd_reply(send_cmd, recvData)
            log.debug('send_cmd : %s', send_cmd)
            log.debug('recvData : %s', recvData)
            pass



    def page_status_change(self):
        if self.page_idx == 0:
            self.page_status.showMessage("Client Page")
        elif self.page_idx == 1:
            self.page_status.showMessage("Meida Page")
        elif self.page_idx == 2:
            self.page_status.showMessage("LED Setting Page")

        '''如果不是在led setting 頁面,把layout視窗關閉'''
        if self.page_idx != 2:
            if self.led_layout_window.isVisible() is True:
                self.led_layout_window.hide()

    
    def set_led_wall_size(self):
        self.led_wall_width = int(self.led_setting_width_editbox.text())
        self.led_wall_height = int(self.led_setting_height_editbox.text())
        log.debug("%d", self.led_wall_width)
        log.debug("%d", self.led_wall_height)
        self.led_layout_window.change_led_wall_res(self.led_wall_width,
                                                   self.led_wall_height,
                                                   default_led_wall_margin)

    '''pop-up cabinet_setting_window while client_layout_tree clicked'''
    def cabinet_setting_window_show(self, a0: QModelIndex)-> None:
        log.debug("%s", self.led_client_layout_tree.itemFromIndex(a0).text(0))
        log.debug("%s", self.led_client_layout_tree.itemFromIndex(a0).parent().text(0))
        client_ip_selected = self.led_client_layout_tree.itemFromIndex(a0).parent().text(0).split("ip:")[1].split(")")[0]
        log.debug(a0.row())
        for c in self.clients:
            if c.client_ip ==client_ip_selected:
                try:
                    if self.cabinet_setting_window is not None:
                        self.cabinet_setting_window.set_params(c.cabinets_setting[a0.row()])
                    else:
                        self.cabinet_setting_window = CabinetSettingWindow(c.cabinets_setting[a0.row()])
                    self.cabinet_setting_window.show()
                except Exception as e:
                    log.error(e)

                break

    def set_cabinet_params(self, c_params):
        log.debug('c_params.client_ip : %s', c_params.client_ip )
        log.debug('c_params.port_id : %d', c_params.port_id)
        for c in self.clients:
            if c.client_ip == c_params.client_ip:
                log.debug('')
                #c.cabinets_setting[c_params.port_id] = c_params
                c.set_cabinets(c_params)


        '''check'''
        for c in self.clients:
            if c.client_ip == c_params.client_ip:
                log.debug("c.cabinets_setting[c_params.port_id].cabinet_width = %d", c.cabinets_setting[c_params.port_id].cabinet_width)
                log.debug("c.cabinets_setting[c_params.port_id].cabinet_height = %d", c.cabinets_setting[c_params.port_id].cabinet_height)
                log.debug("c.cabinets_setting[c_params.port_id].start_x = %d", c.cabinets_setting[c_params.port_id].start_x)
                log.debug("c.cabinets_setting[c_params.port_id].start_y = %d", c.cabinets_setting[c_params.port_id].start_y)

    '''slot for signal_draw_temp_cabinet from cabinet_setting_window'''
    def draw_cabinet_label(self, c_params, qt_line_color):
        if self.led_layout_window is not None:
            log.debug('')
            '''send another signal to led_layout_window to draw the new cabinet layout'''
            self.signal_redraw_cabinet_label.emit(c_params, qt_line_color)
            #self.led_layout_window.redraw_cabinet_label(c_params)

    '''slot for signal_set_default_cabinet_resolution from cabinet_setting_window'''
    def set_default_cabinet_resolution(self, width, height):
        log.debug("")
        for c in self.clients:
            for c_param in c.cabinets_setting:
                c_param.cabinet_width = width
                c_param.cabinet_height = height

    def send_cmd_set_cabinet_params(self, c_params):
        '''select the client'''
        for c in self.clients:
            if c.client_ip is c_params.client_ip:
                str_params = 'port_id:' + str(c_params.port_id) + ',cabinet_width:' + str(c_params.cabinet_width) + \
                             ',cabinet_height:' + str(c_params.cabinet_height) + \
                             ',start_x:' + str(c_params.start_x) + \
                             ',start_y:' + str(c_params.start_y) + \
                             ',layout_type:' + str(c_params.layout_type)

                c.send_cmd(cmd=cmd_set_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(), param=str_params)
                break

    def sync_client_cabinet_params(self, ip, force_or_not):
        ip = "192.168.0.10" #test
        for c in self.clients:
            if c.client_ip == ip:
                for i in range(c.num_of_cabinet):
                    param_str = "port_id:" + str(i)
                    c.send_cmd(cmd=cmd_get_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(), param=param_str)
