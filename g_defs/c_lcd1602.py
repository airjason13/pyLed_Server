import time

from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer
import utils.log_utils
import utils.net_utils
import platform
import sys
import socket
from global_def import *
log = utils.log_utils.logging_init(__file__)

class LCD1602(QObject):

    '''init'''
    def __init__(self, refresh_interval_0,  **kwargs):
        super(LCD1602, self).__init__(**kwargs)

        # line 1/2 refresh interval
        self.refresh_interval_0 = refresh_interval_0

        # line 0/1 content
        self.lcd_data_l0 = []
        self.lcd_data_l1 = []
        self.error_inform_l0 = []
        self.lcd_data_idx = 0
        self.error_inform_idx = 0


        # refresh timer setting
        self.refresh_timer_0 = QTimer(self)
        self.refresh_timer_0.timeout.connect(self.write_lcd_l0)


        self.server_address = lcd1602_server_address
        '''if platform.machine() not in ('arm', 'arm64', 'aarch64'):
            self.socket_connected = False
        else:
            try:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.server_address)
                self.socket_connected = True
                self.socket.close()
            except:
                log.error("lcd1602 server connect failed!")
                self.socket_connected = False'''



    def start(self):
        self.refresh_timer_0.start(self.refresh_interval_0)


    def write_lcd_l0(self):
        # pass data to lcd1602_server
        if platform.machine() not in ('arm', 'arm64', 'aarch64'):
            log.error("Not on aarch64")
            return

        try:
            if len(self.error_inform_l0) != 0:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.server_address)
                message = "0:0:" + self.error_inform_l0[0]
                self.socket.sendall(message.encode())
                self.socket.close()
                self.lcd_data_idx += 1
            else:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.server_address)
                message_line0 = "0:0:" + self.lcd_data_l0[self.lcd_data_idx]
                self.socket.sendall(message_line0.encode())
                self.socket.close()

                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.server_address)
                message_line1 = "0:1:" + self.lcd_data_l1[self.lcd_data_idx]
                self.socket.sendall(message_line1.encode())
                self.socket.close()

                self.lcd_data_idx += 1
                if self.lcd_data_idx >= len(self.lcd_data_l0):
                    self.lcd_data_idx = 0
        except:
            log.error("write_lcd_l0 error")


    def add_data(self, data0, data1):
        self.lcd_data_l0.append(data0)
        self.lcd_data_l1.append(data1)

    def del_data(self, line_num):
        pass