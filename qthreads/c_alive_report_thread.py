import time
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime
from global_def import *
import socket
import utils.log_utils

log = utils.log_utils.logging_init('c_alive_report_thread')

class alive_report_thread(QThread):
    check_client = pyqtSignal(str, str)
    def __init__(self,ip=multicast_group, port=alive_report_port, **kwargs):

        super(alive_report_thread, self).__init__( **kwargs)
        self.recv_ip = ip
        self.recv_port = port
        self.address = (self.recv_ip, self.recv_port)
        #log.debug("self.recv_ip: %s", self.recv_ip)
        #log.debug("self.recv_port: %s", self.recv_port)
        self.num = 0

    def run(self, *args, **kwargs):
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind(self.address)
        self.recv_socket.settimeout(2)
        while True:
            try:
                self.num += 1
                #if(self.num == 5):
                #self.check_client.emit("192.168.0.99")
                data, addr = self.recv_socket.recvfrom(2048)
                if data is not None:
                    log.debug("recv from : %s", addr)
                    #log.debug("recv len: %s", len(data))
                    #log.debug("recv data: %s", data)
                    if "alive" in data.decode():
                        self.check_client.emit(addr[0], data.decode())
                time.sleep(0.001)
            except Exception as e:
                log.error(e)
            time.sleep(0.001)
