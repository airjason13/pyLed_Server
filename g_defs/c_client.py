from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject
import utils.log_utils

log = utils.log_utils.logging_init('c_client')

class client(QObject):
    alive_val_def = 3

    def __init__(self, ip, **kwargs):
        super(client, self).__init__(**kwargs)
        self.client_ip = ip
        self.alive_val = self.alive_val_def

    def send_cmd(self, cmd, param):
        log.debug("client send_cmd")

    def set_alive_count(self, val):
        self.alive_val = val

    def decrese_alive_count(self):
        if self.alive_val > 0:
            self.alive_val -= 1

    def get_alive_count(self):
        return self.alive_val