from PyQt5 import QtCore
from global_def import *


class ApplicationPlugin(QtCore.QThread):
    def __init__(self, app_, port=flask_server_port):
        super(ApplicationPlugin, self).__init__()
        self.app_target = app_
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        log.debug("flask start to run")
        try:
            self.app_target.run(debug=False, host='0.0.0.0', port=self.port, threaded=True)
        finally:
            log.debug("flask End!")
