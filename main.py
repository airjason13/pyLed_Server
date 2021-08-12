# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from c_mainwindow import MainUi
import sys
from PyQt5.QtWidgets import QApplication
import jqlocalserver
import utils.log_utils




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    log = utils.log_utils.logging_init(__file__)
    log.info('Main')

    app = QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    server = jqlocalserver.Server()
    server.dataReceived.connect(gui.parser_cmd_from_qlocalserver)

    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
