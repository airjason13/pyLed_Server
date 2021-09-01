from PyQt5.QtCore import QObject

import utils.log_utils
log = utils.log_utils.logging_init('c_led_params')

class cabinet_params(QObject):
    def __init__(self, client_ip, client_id, port_id,  cabinet_width, cabinet_height, layout_type, start_x, start_y, **kwargs):
        super(cabinet_params, self).__init__(**kwargs)
        self.client_ip = client_ip
        self.client_id = client_id
        self.port_id = port_id
        self.cabinet_width = cabinet_width
        self.cabinet_height = cabinet_height
        self.start_x = start_x
        self.start_y = start_y
        self.layout_type = layout_type