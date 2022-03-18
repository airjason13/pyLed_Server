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

app = Flask(__name__)
from routes import *

#app_ = Flask(__name__)
#from routes import *
#   setting our root
#@app_.route('/')
#def index():
#    return render_template('index.html')

def sighandler(signum, frame):
    log.fatal("Caough signal %d", signum)
    traceback.print_stack(frame)


if __name__ == '__main__':
    log = utils.log_utils.logging_init(__file__)
    log.info('Main')

    global_debug_level = logging.FATAL
    utils.log_utils.set_logging_level(global_debug_level)

    '''Insert signal handler'''
    log.info("Insert signal")
    '''for sig in dir(signal):
        if sig.startswith("SIG"):
            try:
                signum = getattr(signal, sig)
                signal.signal(signum, sighandler)
            except: 
                log.info("Skip %s", sig)'''

    signal.signal(signal.SIGSEGV, sighandler)

    log.info("Insert signal down")

    qt_app = QApplication(sys.argv)

    gui = MainUi()
    gui.show()
    server = jqlocalserver.Server()
    server.dataReceived.connect(gui.parser_cmd_from_qlocalserver)




    #   Preparing parameters for flask to be given in the thread
    #   so that it doesn't collide with main thread
    #kwargs = {'host': '0.0.0.0', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}

    #   running flask thread
    #flaskThread = Thread(target=app_.run, daemon=True, kwargs=kwargs).start()

    flask_app = ApplicationPlugin(app_=app)
    flask_app.start()

    # detect focus on windows or not
    qt_app.focusChanged.connect(gui.focus_on_window_changed)

    sys.exit(qt_app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
