from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer
import utils.log_utils
import utils.net_utils
import platform

log = utils.log_utils.logging_init(__file__)

class Lcd1602(QObject):

    '''init'''
    def __init__(self, refresh_interval_1, refresh_interval_2, **kwargs):
        super(Lcd1602, self).__init__(**kwargs)

        # line 1/2 refresh interval
        self.refresh_interval_1 = refresh_interval_1
        self.refresh_interval_2 = refresh_interval_2

        # line 0/1 content
        self.lcd_data_l0 = []
        self.lcd_data_l1 = []
        self.error_inform_l0 = []
        self.error_inform_l1 = []
        self.lcd_data_l0_idx = 0
        self.lcd_data_l1_idx = 0
        self.error_inform_l0_idx = 0
        self.error_inform_l1_idx = 0

        # refresh timer setting
        self.refresh_timer_0 = QTimer(self)
        self.refresh_timer_0.timeout.connect(self.write_lcd_l0)
        self.refresh_timer_1 = QTimer(self)
        self.refresh_timer_1.timeout.connect(self.write_lcd_l1)


    def write_lcd_l0(self):
        log.debug(" ")
        if platform.machine() not in ('arm', 'arm64', 'aarch64'):
            return
        if len(self.error_inform_l0) != 0:
            pass



    def write_lcd_l1(self):
        log.debug(" ")
        if platform.machine() not in ('arm', 'arm64', 'aarch64'):
            return

    def add_data(self, line_num, data):
        if line_num == 0:
            self.lcd_data_l0.append(data)
        elif line_num == 1:
            self.lcd_data_l1.append(data)