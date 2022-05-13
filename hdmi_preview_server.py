from PyQt5 import QtWidgets, QtCore, QtNetwork
import json
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

SERVER = "hdmi_in_preview_server"


def get_server_name():
    global SERVER
    return SERVER


class PreviewServer(QtNetwork.QLocalServer):
    signal_preview_data_received = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

        if self.isListening():
            log.info("listening")
        else:
            log.debug("not listening")

        if self.hasPendingConnections():
            log.info("has Pending Connections")
        else:
            log.debug("No Pending Connections")

        self.newConnection.connect(self.handle_connection)
        self.removeServer(get_server_name())

        if not self.listen(get_server_name()):
            raise RuntimeError(self.errorString())

    def handle_connection(self):
        data = {}
        socket = self.nextPendingConnection()
        if socket is not None:
            if socket.waitForReadyRead(2000):
                data = json.loads(str(socket.readAll().data(), 'utf-8'))
                # log.debug("data : %s", data)
                socket.disconnectFromServer()
            socket.deleteLater()
        if 'shutdown' in data:
            self.close()
            self.removeServer(self.fullServerName())
            QtWidgets.qApp.quit()
        else:
            # log.debug("data : %s", data)
            self.signal_preview_data_received.emit(data)

    def get_preview_server_full_name(self):
        return self.fullServerName()
