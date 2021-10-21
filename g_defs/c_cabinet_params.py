from PyQt5.QtCore import QObject

import utils.log_utils
log = utils.log_utils.logging_init(__file__)

class cabinet_params(QObject):
    def __init__(self, client_ip, client_id, port_id,
                 cabinet_width, cabinet_height, layout_type, start_x, start_y, **kwargs):
        super(cabinet_params, self).__init__(**kwargs)
        self.client_ip = client_ip
        self.client_id = client_id
        self.port_id = port_id
        self.cabinet_width = cabinet_width
        self.cabinet_height = cabinet_height
        self.start_x = start_x
        self.start_y = start_y
        self.layout_type = layout_type
        self.led_pinch = 8

    def params_to_string(self):
        str_param = "port_id=" + str(self.port_id) + "," +  "cabinet_width=" + str(self.cabinet_width) + "," \
                    + "cabinet_height=" + str(self.cabinet_height) + "," \
                    + "start_x=" + str(self.start_x) + "," \
                    + "start_y=" + str(self.start_y) + "," \
                    + "layout_type=" + str(self.layout_type)
        return str_param

