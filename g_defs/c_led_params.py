from PyQt5.QtCore import QObject
import utils.log_utils
log = utils.log_utils.logging_init('c_led_params')

class client(QObject):

    def __init__(self, led_width, led_height, **kwargs):
        super(client, self).__init__(**kwargs)
        self.led_width = led_width
        self.led_height = led_height
        