from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout, QVBoxLayout,
                            QGridLayout, QFrame,QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                            QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
                             QFileDialog)
from PyQt5.QtGui import QPalette, QColor, QBrush
from PyQt5.QtCore import Qt
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
import numpy as np
import pyqtgraph.exporters as pe
import qdarkstyle, requests, sys, time, random, json, datetime, re
import socket
from time import sleep
from global_def import *
from pyqt_worker import Worker
import netifaces as ni
import utils.net_utils as net_utils
import utils.update_utils as update_utils

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        #pg.setConfigOption('background', '#19232D')
        #pg.setConfigOption('foreground', 'd')
        #pg.setConfigOption('background', '#FD8612')
        #pg.setConfigOption('foreground', '#FD8612')
        pg.setConfigOptions(antialias=True)

        # 窗口居中显示
        self.center()

        self.setWindowOpacity(0.9)  # 设置窗口透明度
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.init_ui()
        self.status = self.statusBar()
        self.status.showMessage("Main Page")

        self.setWindowTitle("LED Server")


        self.broadcast_thread = Worker(method=self.server_broadcast, data="ABCDE", port=server_broadcast_port)
        self.client_alive_thread = Worker(method=self.client_alive_report_thread, port=alive_report_port)
        self.broadcast_thread.start()
        self.client_alive_thread.start()

    def init_ui(self):
        self.setFixedSize(960, 700)

        pagelayout = QGridLayout()

        top_left_frame = QFrame(self)
        top_left_frame.setFrameShape(QFrame.StyledPanel)
        # 　lef layout vertical
        button_layout = QVBoxLayout(top_left_frame)

        btm_left_frame = QFrame(self)
        blank_label = QLabel(btm_left_frame)
        blank_layout = QVBoxLayout(btm_left_frame)
        blank_label.setText("GIS LED")
        blank_label.setFixedHeight(20)
        blank_layout.addWidget(blank_label)

        # btn for connect client
        connect_btn = QPushButton(top_left_frame)
        #connect_btn.setStyleSheet('QPushButton {background-color: #A3C1DA; color: orange;}')
        connect_btn.setFixedSize(200, 30), connect_btn.setText("Connect Client")
        connect_btn.clicked.connect(self.fun_connect_clients)
        button_layout.addWidget(connect_btn)

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

        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)

        # 右边显示为stack布局
        self.right_layout = QStackedLayout(right_frame)

        #qt tree of clients
        self.client_tree = QTreeWidget(right_frame)
        self.client_tree.setColumnCount(3)

        #self.client_tree.setColumnWidth(3,400)
        #self.client_tree.setFixedWidth(500)
        #self.client_tree.setFixedHeight(500)
        #self.client_tree.setHeaderLabels(["ip, id, status"])

        self.client_tree.headerItem().setText(0, "IP")
        self.client_tree.setLineWidth(100)
        self.client_tree.headerItem().setText(1, "ID")
        self.client_tree.headerItem().setText(2, "Status")
        #self.client_tree.setHeaderLabel()

        #test add one client
        root = QTreeWidgetItem(self.client_tree)

        root.setText(0, "192.168.0.52")
        root.setText(1, "0")
        root.setText(2, "connect")
        #child_test = QTreeWidgetItem(root)"""
        self.client_tree.addTopLevelItem(root)

        # test add two client
        root1 = QTreeWidgetItem(self.client_tree)
        self.client_tree.setColumnWidth(3, 400)
        root1.setText(0, "192.168.0.53")
        root1.setText(1, "0")
        root1.setText(2, "connect")
        self.client_tree.addTopLevelItem(root1)

        child_test = QTreeWidgetItem(root)

        client_widget = QWidget(right_frame)
        client_layout = QVBoxLayout()
        client_widget.setLayout(client_layout)
        client_layout.addWidget(self.client_tree)
        self.right_layout.addWidget(client_widget)


        # Test register
        user_line = QLineEdit(right_frame)
        user_line.setPlaceholderText("输入账号：")
        user_line.setFixedWidth(400)
        password_line = QLineEdit(right_frame)
        password_line.setPlaceholderText("请输入密码：")
        password_line.setFixedWidth(400)
        login_layout = QVBoxLayout()
        login_widget = QWidget(right_frame)
        login_widget.setLayout(login_layout)
        login_layout.addWidget(user_line)
        login_layout.addWidget(password_line)
        self.right_layout.addWidget(login_widget)



        self.splitter1 = QSplitter(Qt.Vertical)
        top_left_frame.setFixedHeight(250)
        top_left_frame.setFixedWidth(250)
        self.splitter1.addWidget(top_left_frame)
        self.splitter1.addWidget(btm_left_frame)

        self.splitter2 = QSplitter(Qt.Horizontal)
        self.splitter2.addWidget(self.splitter1)
        # 　add right layout frame
        self.splitter2.addWidget(right_frame)

        # 窗口部件添加布局
        widget = QWidget()
        pagelayout.addWidget(self.splitter2)
        widget.setLayout(pagelayout)

        self.setCentralWidget(widget)


    def center(self):
        '''
        get the geomertry of the screen and set the postion in the center of screen
        '''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def fun_connect_clients(self):
        print("connect clients")

        self.right_layout.setCurrentIndex(0)

    def func_file_contents(self):
        print("file contents")

        self.right_layout.setCurrentIndex(1)

    def func_testA(self):
        print("testA")
        self.right_layout.setCurrentIndex(2)
        file = QFileDialog().getOpenFileName()
        print("file_uri:", file[0])
        update_utils.upload_client_image(file[0])

    def func_testB(self):
        print("testB")

        self.right_layout.setCurrentIndex(3)

    """ handle the command from qlocalserver"""
    def parser_cmd_from_qlocalserver(self, data):
        print("data : ", data)


    """ recv alive report """
    def client_alive_report_thread(self, args):
        port = args.get("port")
        #print("port : ", port)
        #print("client_alive_report_thread")
        sleep(4)

    """send broadcast on eth0"""
    def server_broadcast(self, arg):
        data = arg.get("data")
        port = arg.get("port")
        #print("data :", data)
        #print("port :", port)
        #ni.ifaddresses('enp8s0')
        #ip = ni.ifaddresses('enp8s0')[ni.AF_INET][0]['addr']
        if sys.platform in ('arm', 'arm64', 'aarch64'):
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