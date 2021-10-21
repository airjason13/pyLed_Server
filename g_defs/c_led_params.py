from PyQt5.QtCore import QObject
import utils.log_utils
log = utils.log_utils.logging_init(__file__)

class led_params(QObject):
    def __init__(self, led_width, led_height, **kwargs):
        super(led_params, self).__init__(**kwargs)
        self.led_width = led_width
        self.led_height = led_height
        