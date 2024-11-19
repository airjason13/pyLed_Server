# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from c_mainwindow import MainUi
import sys
from PyQt5.QtWidgets import QApplication
import jqlocalserver
import utils.log_utils
import signal
import logging
from flask import Flask
from application_plugin import *
from threading import Thread
import faulthandler

faulthandler.enable()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
from routes import *


def sighandler(signum, frame):
    log.fatal("Catch signal %d", signum)
    traceback.print_stack(frame)


if __name__ == '__main__':
    # log = utils.log_utils.logging_init(__file__)
    log.info('===============================================Main===================================================')

    sys.setrecursionlimit(100000)

    # global_debug_level = logging.FATAL
    # utils.log_utils.set_logging_level(global_debug_level)



    '''Insert signal handler'''
    signal.signal(signal.SIGSEGV, sighandler)

    qt_app = QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    server = jqlocalserver.Server()
    server.dataReceived.connect(gui.parser_cmd_from_qlocalserver)

    flask_app = ApplicationPlugin(app_=app)
    flask_app.start()



    # detect focus on windows or not
    qt_app.focusChanged.connect(gui.focus_on_window_changed)

    sys.exit(qt_app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
