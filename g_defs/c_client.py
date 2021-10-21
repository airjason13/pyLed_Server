from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject
from PyQt5.QtWidgets import QMessageBox, QFrame, QLabel
from PyQt5.QtCore import Qt, QMutex, pyqtSlot
import qdarkstyle
import utils.log_utils
import utils.net_utils
from g_defs.c_cabinet_params import cabinet_params
from global_def import *
import threading
import asyncio
from commands_def import *

log = utils.log_utils.logging_init(__file__)

class client(QObject):
    alive_val_def = 2
    ''' ret, send_cmd, recv_data, client_ip, client_reply_port '''
    signal_send_cmd_ret = pyqtSignal(bool, str, str, str, int)
    ''' send signal while cabinet params changed from cabinet setting window'''
    signal_cabinet_params_changed = pyqtSignal(cabinet_params)
    ''' send signal while get cabinet signal from cabinet '''
    signal_sync_cabinet_params = pyqtSignal(cabinet_params)

    '''init'''
    def __init__(self, client_ip, server_ip, client_version, client_id, **kwargs):
        super(client, self).__init__(**kwargs)

        self.client_ip = client_ip
        self.server_ip = server_ip
        self.client_udp_cmd_port = g_client_udp_cmd_port
        self.client_version = client_version
        self.client_id = client_id

        self.alive_val = self.alive_val_def
        self.id = -1
        self.loop = asyncio.get_event_loop()

        self.num_of_cabinet = 8
        self.cabinets_setting = []
        for i in range(self.num_of_cabinet):
            '''client_ip, client_id, port_id, cabinet_width, cabinet_height, layout_type, start_x, start_y'''
            cabinet_setting = cabinet_params(self.client_ip, 0, i, 0, 0, 0, 1, 1)
            self.cabinets_setting.append(cabinet_setting)




    def send_cmd(self,  cmd, cmd_seq_id, param):
        log.debug("client send_cmd")
        thread_cmd = threading.Thread(target=utils.net_utils.send_udp_cmd,
                                      kwargs={'cmd':cmd, 'cmd_seq_id':cmd_seq_id, 'param': param,
                                              'client_ip': self.client_ip, 'client_udp_cmd_port': self.client_udp_cmd_port,
                                              'server_ip': self.server_ip, 'cb': self.send_cmd_callback})
        thread_cmd.start()

    def set_alive_count(self, val):
        self.alive_val = val

    def decrese_alive_count(self):
        if self.alive_val > 0:
            self.alive_val -= 1

    def get_alive_count(self):
        return self.alive_val

    def send_cmd_callback(self, ret, send_cmd, recvData=None, client_ip=None, client_reply_port=None ):
        #self.cmd_cb(ret, recvData, client_ip, client_reply_port)
        self.signal_send_cmd_ret.emit(ret, send_cmd, recvData, self.client_ip, client_reply_port)


    def get_client_version(self):
        return self.client_version

    def set_client_version(self, version):
        self.client_version = version

    def set_cabinets(self, c_params):

        self.cabinets_setting[c_params.port_id].cabinet_width = c_params.cabinet_width
        self.cabinets_setting[c_params.port_id].cabinet_height = c_params.cabinet_height
        self.cabinets_setting[c_params.port_id].start_x = c_params.start_x
        self.cabinets_setting[c_params.port_id].start_y = c_params.start_y
        self.cabinets_setting[c_params.port_id].layout_type = c_params.layout_type

        '''test send cmd with signal_cabinet_params_changed signal/slot'''
        self.signal_cabinet_params_changed.emit(self.cabinets_setting[c_params.port_id])

    def parse_get_cmd_reply_get_cabinet_params(self, cmd, recv_data):
        try:
            data = recv_data.split(";")[2].split(":")[1]
            print(data)
            str_params = data.split(",")
            for s in str_params:
                if s.startswith("port_id"):
                    port_id = int(s.split("port_id=")[1])
                elif s.startswith("cabinet_width"):
                    cabinet_width = int(s.split("cabinet_width=")[1])
                elif s.startswith("cabinet_height"):
                    cabinet_height = int(s.split("cabinet_height=")[1])
                elif s.startswith("start_x"):
                    start_x = int(s.split("start_x=")[1])
                elif s.startswith("start_y"):
                    start_y = int(s.split("start_y=")[1])
                elif s.startswith("layout_type"):
                    layout_type = int(s.split("layout_type=")[1])
            """log.debug("port_id: %d", port_id)
            log.debug("cabinet_width: %d", cabinet_width)
            log.debug("cabinet_height: %d", cabinet_height)
            log.debug("start_x: %d", start_x)
            log.debug("start_y: %d", start_y)
            log.debug("layout_type: %d", layout_type)"""
            self.cabinets_setting[port_id].cabinet_width = cabinet_width
            self.cabinets_setting[port_id].cabinet_height = cabinet_height
            self.cabinets_setting[port_id].start_x = start_x
            self.cabinets_setting[port_id].start_y = start_y
            self.cabinets_setting[port_id].layout_type = layout_type
            self.signal_sync_cabinet_params.emit(self.cabinets_setting[port_id])


        except Exception as e:
            log.fatal(e)

    def parse_get_cmd_reply(self, cmd, recv_data):
        if cmd == cmd_get_cabinet_params:
            self.parse_get_cmd_reply_get_cabinet_params(cmd, recv_data)

