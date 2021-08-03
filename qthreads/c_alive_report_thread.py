import time
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime
from global_def import *
import socket


class alive_report_thread(QThread):
    check_client = pyqtSignal(str)
    def __init__(self,ip=multicast_group, port=alive_report_port, **kwargs):

        super(alive_report_thread, self).__init__( **kwargs)
        self.recv_ip = ip
        self.recv_port = port
        self.address = (self.recv_ip, self.recv_port)
        print("self.recv_ip:", self.recv_ip)
        print("self.recv_port:", self.recv_port)
        self.num = 0

    def run(self, *args, **kwargs):
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind(self.address)
        while True:
            self.num += 1
            #if(self.num == 5):
            #self.check_client.emit("192.168.0.99")
            data, addr = self.recv_socket.recvfrom(2048)
            if data is not None:
                print("recv from :", addr)
                print("recv len:", len(data))
                print("recv data:", data)
                if data.decode() == "alive":
                    self.check_client.emit(addr[0])
            time.sleep(0.001)
