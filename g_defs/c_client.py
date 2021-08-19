from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject
from PyQt5.QtWidgets import QMessageBox
import qdarkstyle
import utils.log_utils
import utils.net_utils
from global_def import *
import threading

log = utils.log_utils.logging_init('c_client')

class client(QObject):
    alive_val_def = 3
    ''' ret, send_cmd, recv_data, client_ip, client_reply_port '''
    send_cmd_ret = pyqtSignal(bool, str, str, str, int)
    def __init__(self, client_ip, server_ip, client_version, client_id, **kwargs):
        super(client, self).__init__(**kwargs)

        self.client_ip = client_ip
        self.server_ip = server_ip
        self.client_udp_cmd_port = g_client_udp_cmd_port
        self.client_version = client_version
        self.client_id = client_id

        self.alive_val = self.alive_val_def
        self.id = -1

    def send_cmd(self,  cmd, cmd_seq_id, param):
        log.debug("client send_cmd")
        thread_cmd = threading.Thread(target=utils.net_utils.send_udp_cmd,
                                      kwargs={'cmd':cmd, 'cmd_seq_id':cmd_seq_id, 'param': param,
                                              'client_ip': self.client_ip, 'client_udp_cmd_port': self.client_udp_cmd_port,
                                              'server_ip': self.server_ip, 'cb': self.send_cmd_callback})
        thread_cmd.start()
        #utils.net_utils.send_udp_cmd( mainUI, cmd, cmd_seq_id, param, cb)
        thread_cmd.join()
    def set_alive_count(self, val):
        self.alive_val = val

    def decrese_alive_count(self):
        if self.alive_val > 0:
            self.alive_val -= 1

    def get_alive_count(self):
        return self.alive_val

    def send_cmd_callback(self, ret, send_cmd, recvData=None, client_ip=None, client_reply_port=None ):
        #self.cmd_cb(ret, recvData, client_ip, client_reply_port)
        self.send_cmd_ret.emit(ret, send_cmd, recvData, self.client_ip, client_reply_port)
        '''if recvData is not None:
            log.debug("recvData : %s", recvData)
            log.debug("client_ip : %s", client_ip)
            log.debug("client_reply_port : %d", client_reply_port )

        if ret is False:
            log.fatal("ret :%s", ret)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(recvData)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            msg.exec_()'''

    def get_client_version(self):
        return self.client_version

    def set_client_version(self, version):
        self.client_version = version