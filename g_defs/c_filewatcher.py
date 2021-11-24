import os.path
import signal
import time
import threading
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer, QFileSystemWatcher
import pyinotify
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class FileWatcher(QObject):
    signal_folder_changed = pyqtSignal(str)
    def __init__(self, paths, **kwargs):
        super(FileWatcher, self).__init__(**kwargs)
        self.watch_paths = paths
        self.watcher = QFileSystemWatcher(self.watch_paths)
        self.watcher.directoryChanged.connect(self.directory_changed)

    def directory_changed(self, path):
        log.debug("path :%s", path)
        self.signal_folder_changed.emit(path)

    def install_folder_changed_slot(self, qt_slot):
        log.debug("")
        self.signal_folder_changed.connect(qt_slot)
'''
class OnIOHandler:
    pass


class FileWatcher(QObject):

    def __init__(self, paths, **kwargs):
        super(FileWatcher, self).__init__(**kwargs)
        self.watch_paths = paths
        self.wm = pyinotify.WatchManager()
        # mask = pyinotify.EventsCodes.ALL_FLAGS.get('IN_CREATE', 0)
        # mask = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']                             # 監控內容，只監聽檔案被完成寫入
        self.mask = pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.OnIOHandler())  # 回撥函式
        self.notifier.start()
        for path in self.watch_paths:
            self.wm.add_watch(path, self.mask, rec=True, auto_add=True)

    def file_close_write(self):
        log.debug("")


    # 事件回撥函式
    class OnIOHandler(pyinotify.ProcessEvent):
        
    
        # 重寫檔案寫入完成函式
        def process_IN_CLOSE_WRITE(self, event):
            file_path = os.path.join(event.path, event.name)
            print('檔案完成寫入', file_path)

        # 重寫檔案刪除函式
        def process_IN_DELETE(self, event):
            print("檔案刪除: %s " % os.path.join(event.path, event.name))

        # 重寫檔案改變函式
        def process_IN_MODIFY(self, event):
            print("檔案改變: %s " % os.path.join(event.path, event.name))

        # 重寫檔案建立函式
        def process_IN_CREATE(self, event):
            print("檔案建立: %s " % os.path.join(event.path, event.name))'''
