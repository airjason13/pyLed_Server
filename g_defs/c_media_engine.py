import os.path
import signal
import time
import threading
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer, QMutex
from utils.ffmpy_utils import *
import utils.log_utils
from utils.file_utils import *
from pyudev import Context, Monitor, MonitorObserver
from g_defs.c_video_params import *
from g_defs.c_led_config import *
import random

from global_def import *


class media_engine(QObject):
    ''' changed_or_not, playlist_name, file_uri, "add" or "del" '''
    signal_playlist_changed_ret = pyqtSignal(bool, str, str, int, str)
    ''' changed_or_not '''
    signal_external_medialist_changed_ret = pyqtSignal(bool)
    ''' play status changed '''
    signal_play_status_changed = pyqtSignal(bool, int)

    '''Action TAG'''
    ACTION_TAG_ADD_MEDIA_FILE = "add_media_file"
    ACTION_TAG_REMOVE_MEDIA_FILE = "remove_media_file"
    ACTION_TAG_REMOVE_ENTIRE_PLAYLIST = "remove_entire_playlist"
    ACTION_TAG_ADD_NEW_PLAYLIST = "add_playlist"

    '''init'''

    def __init__(self, led_config, **kwargs):
        super(media_engine, self).__init__(**kwargs)
        self.internal_medialist = medialist(internal_media_folder)

        ''' handle the external media list'''
        # self.external_mount_points = get_mount_points()
        self.led_config = led_config
        self.external_medialist = []
        for mount_point in utils.file_utils.get_mount_points():
            external_medialist_tmp = medialist(mount_point)
            self.external_medialist.append(external_medialist_tmp)

        '''handle the playlist'''
        self.playlist_files = get_playlist_file_list(internal_media_folder + PlaylistFolder)
        log.debug(self.playlist_files)
        self.playlist = []
        for file in self.playlist_files:
            playlist_tmp = playlist(file)
            self.playlist.append(playlist_tmp)

        '''init usb monitor'''
        self.init_usb_monitor()

        '''media_process'''
        self.media_processor = media_processor(self.led_config)
        self.media_processor.signal_media_play_status_changed.connect(self.play_status_changed)
        '''hdmi-in cast'''

    def sync_playlist(self):
        self.playlist_files = get_playlist_file_list(internal_media_folder + PlaylistFolder)
        log.debug(self.playlist_files)
        self.playlist = []
        for file in self.playlist_files:
            playlist_tmp = playlist(file)
            self.playlist.append(playlist_tmp)
        log.debug("self.playlist = %s", self.playlist)

    # hdmi_in_src : string
    # cast_dst : array of string
    def start_hdmi_in_v4l2(self, hdmi_in_src, cast_dst):
        log.debug("")
        if os.path.exists(hdmi_in_src) is False:
            log.error("%s is not exist", hdmi_in_src)
            return None
        return self.media_processor.hdmi_in_cast_v4l2(hdmi_in_src, cast_dst)

    def start_hdmi_in_h264(self, hdmi_in_src, cast_dst):
        log.debug("")
        if os.path.exists(hdmi_in_src) is False:
            log.error("%s is not exist", hdmi_in_src)
            return None
        return self.media_processor.hdmi_in_cast_h264(hdmi_in_src, cast_dst)

    def play_single_file(self, file_uri):
        log.debug("")
        self.stop_play()
        if os.path.exists(file_uri) is False:
            log.error("%s is not exist", file_uri)
        self.media_processor.single_play(file_uri)

    def play_playlist(self, playlist_name):
        log.debug("playlist_name = %s", playlist_name)
        self.stop_play()
        for pl in self.playlist:
            if pl.name == playlist_name:
                log.debug("find playlist with playlist_name = %s", playlist_name)
                self.media_processor.playlist_play(pl)

    def stop_play(self):
        self.media_processor.stop_playing()

    def pause_play(self):
        self.media_processor.pause_playing()

    def resume_play(self):
        self.media_processor.resume_playing()

    def play_status_changed(self, status_changed, status):
        self.signal_play_status_changed.emit(status_changed, status)

    def init_usb_monitor(self):
        context = Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        observer = MonitorObserver(monitor,
                                   callback=self.print_device_event,
                                   name='monitor-observer')
        observer.daemon
        observer.start()

    def add_external_medialist(self, uri):
        log.debug("uri : %s", uri)
        for external_media_list in self.external_medialist:
            if external_media_list.folder_uri == uri:
                log.debug("already have this one!")
                return

        external_media_list = medialist(uri)
        self.external_medialist.append(external_media_list)

    def add_to_playlist(self, playlist_name, media_file_uri):
        playlist_folder_path = internal_media_folder + "/.playlists"
        if not os.path.exists(playlist_folder_path):
            os.makedirs(playlist_folder_path)

        log.debug("playlist_name : %s", playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0,
                                                      self.ACTION_TAG_ADD_MEDIA_FILE)
                return

        '''在這邊表示playlist_name 為新創建的,不在原本的playlist array裏面'''
        self.new_playlist(playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0,
                                                      self.ACTION_TAG_ADD_NEW_PLAYLIST)
                return

    def remove_from_playlist(self, playlist_name, index):
        log.debug("remove_from_playlist index :%d", index)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                for i in playlist.fileslist:
                    log.debug("%s", i)
                media_file_uri = playlist.fileslist[index]
                del playlist.fileslist[index]
                playlist.playlist_sync_file()
                for i in playlist.fileslist:
                    log.debug("%s", i)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, index,
                                                      self.ACTION_TAG_REMOVE_MEDIA_FILE)

    def print_device_event(self, device):
        sleep(3)  # time for waiting mount
        mount_points = get_mount_points()
        '''用mount points 長度判斷是否要改變external_medialist'''
        if len(mount_points) != len(self.external_medialist):
            del self.external_medialist
            self.external_medialist = []
            for uri in mount_points:
                log.debug("uri : %s", uri)
                self.add_external_medialist(uri)
            self.signal_external_medialist_changed_ret.emit(True)

    def new_playlist(self, new_playlist_name):
        # new_playlist_name += ".playlist"
        new_playlist = playlist(internal_media_folder + PlaylistFolder + new_playlist_name)
        new_playlist.playlist_sync_file()
        self.playlist.append(new_playlist)

    def del_playlist(self, remove_playlist_name):
        index = -1
        playlist_len = len(self.playlist)
        log.debug("playlist_len : %d", playlist_len)
        for i in range(playlist_len):
            if self.playlist[i].name == remove_playlist_name:
                index = i
                break

        if index != -1:
            self.playlist[index].del_playlist_file()
            del self.playlist[index]
            self.signal_playlist_changed_ret.emit(True, remove_playlist_name, "", 0,
                                                  self.ACTION_TAG_REMOVE_ENTIRE_PLAYLIST)

    def refresh_internal_medialist(self):
        del self.internal_medialist
        self.internal_medialist = medialist(internal_media_folder)

class medialist(QObject):
    def __init__(self, uri):
        self.folder_uri = uri
        self.filelist = utils.file_utils.get_media_file_list(self.folder_uri)


class playlist(QObject):
    def __init__(self, name):
        self.name_with_path = name
        self.name = os.path.basename(self.name_with_path)
        self.fileslist = []
        if os.path.exists(self.name_with_path):
            self.load_playlist(self.name_with_path)
        else:
            self.add_file_uri_to_playlist(None)

    def load_playlist(self, file_uri):
        file = open(file_uri, 'r')
        lines = file.readlines()
        for line in lines:
            if len(line) > 1:
                self.fileslist.append(line.strip())

    def add_file_uri_to_playlist(self, file_uri):
        if file_uri is not None:
            self.fileslist.append(file_uri)
            self.playlist_sync_file()
        else:
            file = open(self.name_with_path, "w")
            file.truncate()

    def playlist_sync_file(self):
        file = open(self.name_with_path, "w")
        for i in self.fileslist:
            file.write(i + "\n")
        file.truncate()

    def del_playlist_file(self):
        log.debug("del_playlist_file")
        if os.path.exists(self.name_with_path):
            log.debug("del playlist : %s", self.name_with_path)
            os.remove(self.name_with_path)

    def __del__(self):
        log.debug("playlist del")


class media_processor(QObject):
    signal_media_play_status_changed = pyqtSignal(bool, int)
    signal_play_hdmi_in_start_ret = pyqtSignal()
    signal_play_hdmi_in_finish_ret = pyqtSignal()

    def __init__(self, led_config):
        super(media_processor, self).__init__()
        self.led_config = led_config
        self.output_width = self.led_config.get_led_wall_width()   # default_led_wall_width
        self.output_height = self.led_config.get_led_wall_height()  # default_led_wall_height
        self.play_status = play_status.stop
        self.pre_play_status = play_status.initial
        self.play_type = play_type.play_none
        self.repeat_option = repeat_option.repeat_all
        self.play_single_file_thread = None
        self.ffmpy_process = None
        self.playing_file_name = None
        self.video_params = video_params(True, 20, 50, 0, 0, 0, 2.2)

        # self.check_ffmpy_process_timer = QTimer(self)
        # self.check_ffmpy_process_timer.timeout.connect(self.check_ffmpy_process)  # 當時間到時會執行 run
        # self.check_ffmpy_process_timer.start(1000)

        self.check_play_status_timer = QTimer(self)
        self.check_play_status_timer.timeout.connect(self.check_play_status)  # 當時間到時會執行 run
        try:
            self.check_play_status_timer.start(500)
        except Exception as e:
            log.debug(e)

        self.play_single_file_worker = None
        self.play_single_file_thread = None
        self.play_playlist_worker = None
        self.play_playlist_thread = None
        self.play_hdmi_in_worker = None
        self.play_hdmi_in_thread = None
        self.play_cms_worker = None
        self.play_cms_thread = None

        self.play_mutex = QMutex()

        ''' this is only cast /dev/video0 to others for preview'''
        self.hdmi_in_cast_process = None

    def set_repeat_option(self, option):
        if option < repeat_option.repeat_none \
                or option > repeat_option.repeat_option_max:
            log.error("repeat_option out of range")
            return
        self.repeat_option = option
        log.debug("self.repeat_option : %d", self.repeat_option)

    def set_output_resolution(self, width, height):
        self.output_width = width
        self.output_height = height

    def stop_playing(self):
        log.debug("")
        self.play_mutex.lock()
        if True: #self.play_status != play_status.stop:
            try:
                os.popen("pkill -f play_hdmi_in_audio.sh")
                os.popen("pkill -f arecord")
                os.popen("pkill -f aplay")

                if self.play_single_file_worker is not None:
                    # self.play_single_file_thread.quit()
                    self.play_single_file_worker.stop()
                    if self.ffmpy_process is not None:
                        if platform.machine() in ('arm', 'arm64', 'aarch64'):
                            os.popen("kill -9 $(pgrep -f h264_v4l2m2m)")
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                            # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                        else:
                            os.popen("kill -9 $(pgrep -f libx264)")
                        #os.kill(self.ffmpy_process.pid, signal.SIGTERM)

                    log.debug("single_file_worker is not None A1")
                    try:
                        if self.play_single_file_thread is not None:
                            self.play_single_file_thread.quit()
                        # self.play_single_file_worker.finished.emit()
                        for i in range(10):
                            log.debug("self.play_single_file_thread.isFinished() = %d", self.play_single_file_thread.isFinished())
                            if self.play_single_file_thread.isFinished() is True:
                                break
                            time.sleep(1)
                    
                        log.debug("single_file_worker is not None A2")
                        self.play_single_file_thread.wait()
                        self.play_single_file_thread.exit(0)
                    except Exception as e:
                        log.debug(e)
                    # self.play_single_file_worker.stop()
                    # del self.play_single_file_worker
                    # del self.play_single_file_thread
                    self.play_single_file_worker = None
                    self.play_single_file_thread = None
                if self.play_playlist_worker is not None:
                    # self.play_playlist_thread.quit()
                    #self.play_playlist_worker.finished.emit()
                    self.play_playlist_worker.stop()
                    if self.ffmpy_process is not None:
                        if platform.machine() in ('arm', 'arm64', 'aarch64'):
                            os.popen("kill -9 $(pgrep -f h264_v4l2m2m)")
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                        else:
                            os.popen("kill -9 $(pgrep -f libx264)")
                        # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                    # self.play_single_file_thread.quit()
                    self.play_playlist_thread.quit()
                    # self.play_single_file_worker.finished.emit()
                    for i in range(10):
                        log.debug("self.play_playlist_thread.isFinished() = %d",
                                  self.play_playlist_thread.isFinished())
                        if self.play_playlist_thread.isFinished() is True:
                            break
                        time.sleep(1)
                    self.play_playlist_thread.wait()
                    self.play_playlist_thread.exit(0)

                    # del self.play_playlist_worker
                    # del self.play_single_file_thread
                    self.play_playlist_worker = None
                    self.play_playlist_thread = None
                if self.play_hdmi_in_worker is not None:

                    self.play_hdmi_in_worker.stop()
                    if self.ffmpy_process is not None:
                        if platform.machine() in ('arm', 'arm64', 'aarch64'):
                            os.popen("kill -9 $(pgrep -f h264_v4l2m2m)")
                        else:
                            os.popen("kill -9 $(pgrep -f libx264)")
                        # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                    self.play_hdmi_in_thread.quit()
                    for i in range(10):
                        log.debug("self.play_hdmi_in_thread.isFinished() = %d",
                                  self.play_hdmi_in_thread.isFinished())
                        if self.play_hdmi_in_thread.isFinished() is True:
                            break
                        time.sleep(1)

                    self.play_hdmi_in_thread.wait()
                    self.play_hdmi_in_thread.exit(0)

                    # del self.play_hdmi_in_worker
                    # del self.play_hdmi_in_thread
                    self.play_hdmi_in_worker = None
                    self.play_hdmi_in_thread = None
                if self.play_cms_worker is not None:
                    # self.play_hdmi_in_thread.quit()
                    # self.play_cms_worker.signal_play_cms_finish.emit()
                    self.play_cms_worker.stop()
                    if self.ffmpy_process is not None:
                        if platform.machine() in ('arm', 'arm64', 'aarch64'):
                            os.popen("kill -9 $(pgrep -f h264_v4l2m2m)")
                        else:
                            os.popen("kill -9 $(pgrep -f libx264)")
                        # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                    self.play_cms_thread.quit()
                    for i in range(10):
                        log.debug("self.play_cms_thread.isFinished() = %d",
                                  self.play_cms_thread.isFinished())
                        if self.play_cms_thread.isFinished() is True:
                            break
                        time.sleep(1)

                    self.play_cms_thread.wait()
                    self.play_cms_thread.exit(0)
                    # self.play_cms_worker.stop()
                    # del self.play_cms_worker
                    self.play_cms_worker = None
                    self.play_cms_thread = None

            except Exception as e:
                log.debug(e)
        
        self.play_mutex.unlock()


    def pause_playing(self):
        if self.play_status != play_status.stop:
            try:
                if self.ffmpy_process is not None:
                    os.kill(self.ffmpy_process.pid, signal.SIGSTOP)
                    self.play_status = play_status.pausing
            except Exception as e:
                log.debug(e)

    def resume_playing(self):
        if self.play_status != play_status.stop:
            try:
                if self.ffmpy_process is not None:
                    os.kill(self.ffmpy_process.pid, signal.SIGCONT)
                    self.play_status = play_status.playing
            except Exception as e:
                log.debug(e)

    def single_play(self, file_uri):
        log.debug("")

        try:
            if self.play_single_file_worker is not None:
                if self.play_single_file_worker.get_task_status() == 1:
                    log.debug("still got file playing!")
                    self.stop_playing()
                    # self.play_mutex.unlock()
                    return 
        except Exception as e:
            log.debug(e)

        self.play_single_file_thread = QThread()

        self.play_single_file_worker = self.play_single_file_work(self, file_uri, 5)
        self.play_single_file_worker.moveToThread(self.play_single_file_thread)
        self.play_single_file_thread.started.connect(self.play_single_file_worker.run)
        self.play_single_file_worker.finished.connect(self.play_single_file_thread.quit)
        self.play_single_file_worker.finished.connect(self.play_single_file_worker.deleteLater)
        self.play_single_file_thread.finished.connect(self.play_single_file_thread.deleteLater)
        self.play_single_file_thread.start()
        # If add .exec() on qthread, the process will hang here
        # self.play_single_file_thread.exec()
        # self.play_mutex.unlock()

    def playlist_play(self, playlist):
        log.debug("")
        try:
            if self.play_playlist_worker is not None:

                if self.play_playlist_worker.get_task_status() == 1:
                    log.debug("still got playlist playing!")
                    self.stop_playing()

                    return
        except Exception as e:
            log.debug(e)

        self.play_playlist_thread = QThread()
        self.play_playlist_worker = self.play_playlist_work(self, playlist, 5)
        self.play_playlist_worker.moveToThread(self.play_playlist_thread)
        self.play_playlist_thread.started.connect(self.play_playlist_worker.run)
        self.play_playlist_worker.finished.connect(self.play_playlist_thread.quit)
        self.play_playlist_worker.finished.connect(self.play_playlist_worker.deleteLater)
        self.play_playlist_thread.finished.connect(self.play_playlist_thread.deleteLater)
        self.play_playlist_thread.start()
        # If add .exec() on qthread, the process will hang here
        # self.play_playlist_thread.exec()

    def hdmi_in_play(self, video_src, video_dst):
        try:
            if self.play_hdmi_in_worker is not None:

                if self.play_hdmi_in_worker.get_task_status() == 1:
                    log.debug("still got hdmi-in playing!")
                    self.stop_playing()
                    # self.play_mutex.unlock()
                    return
        except Exception as e:
            log.debug(e)

        self.play_hdmi_in_thread = QThread()
        self.play_hdmi_in_worker = self.play_hdmi_in_work(self, video_src, video_dst)
        self.play_hdmi_in_worker.signal_play_hdmi_in_start.connect(self.play_hdmi_in_start_ret)
        self.play_hdmi_in_worker.signal_play_hdmi_in_finish.connect(self.play_hdmi_in_finish_ret)
        self.play_hdmi_in_worker.moveToThread(self.play_hdmi_in_thread)
        self.play_hdmi_in_thread.started.connect(self.play_hdmi_in_worker.run)
        self.play_hdmi_in_worker.signal_play_hdmi_in_finish.connect(self.play_hdmi_in_thread.quit)
        self.play_hdmi_in_worker.signal_play_hdmi_in_finish.connect(self.play_hdmi_in_worker.deleteLater)
        self.play_hdmi_in_thread.finished.connect(self.play_hdmi_in_thread.deleteLater)
        self.play_hdmi_in_thread.start()
        # If add .exec() on qthread, the process will hang here
        # self.play_hdmi_in_thread.exec()

    def cms_play(self, window_width, window_height, window_x, window_y, video_dst):
        #log.debug("%s", video_dst)
        try:
            if self.play_hdmi_in_worker is not None:

                if self.play_hdmi_in_worker.get_task_status() == 1:
                    log.debug("still got hdmi-in playing!")
                    self.stop_playing()
                    # self.play_mutex.unlock()
                    return
        except Exception as e:
            log.debug(e)

        # if self.play_hdmi_in_thread is not None:
        #    self.play_hdmi_in_thread.finished()
        #    self.play_hdmi_in_thread.deleteLater()

        self.play_cms_thread = QThread()
        self.play_cms_worker = self.play_cms_work(self, window_width, window_height, window_x, window_y, video_dst)
        self.play_cms_worker.signal_play_cms_start.connect(self.play_hdmi_in_start_ret)
        self.play_cms_worker.signal_play_cms_finish.connect(self.play_hdmi_in_finish_ret)
        self.play_cms_worker.moveToThread(self.play_cms_thread)
        self.play_cms_thread.started.connect(self.play_cms_worker.run)
        self.play_cms_worker.signal_play_cms_finish.connect(self.play_cms_thread.quit)
        self.play_cms_worker.signal_play_cms_finish.connect(self.play_cms_worker.deleteLater)
        self.play_cms_thread.finished.connect(self.play_cms_thread.deleteLater)
        self.play_cms_thread.start()
        # If add .exec() on qthread, the process will hang here
        # self.play_cms_thread.exec()

    def play_hdmi_in_start_ret(self):
        self.signal_play_hdmi_in_start_ret.emit()

    def play_hdmi_in_finish_ret(self):
        self.signal_play_hdmi_in_finish_ret.emit()

    def hdmi_in_cast_h264(self, hdmi_in_src, cast_dst):
        self.hdmi_in_cast_process = \
            neo_ffmpy_cast_video_h264(hdmi_in_src, cast_dst,
                              self.video_params.get_translated_brightness(),
                              self.video_params.get_translated_contrast(),
                              self.video_params.get_translated_redgain(),
                              self.video_params.get_translated_greengain(),
                              self.video_params.get_translated_bluegain(),
                              160,
                              120 )
                              #self.output_width,
                              #self.output_height )
        log.debug("self.hdmi_in_cast_process.pid = %d", self.hdmi_in_cast_process.pid)
        return self.hdmi_in_cast_process

    def hdmi_in_cast_v4l2(self, hdmi_in_src, cast_dst):
        self.hdmi_in_cast_process = \
            neo_ffmpy_cast_video_v4l2(hdmi_in_src, cast_dst,
                              self.video_params.get_translated_brightness(),
                              self.video_params.get_translated_contrast(),
                              self.video_params.get_translated_redgain(),
                              self.video_params.get_translated_greengain(),
                              self.video_params.get_translated_bluegain(),
                              self.output_width,
                              self.output_height )
        #log.debug("self.hdmi_in_cast_process.pid = %d", self.hdmi_in_cast_process.pid)
        return self.hdmi_in_cast_process

    '''檢查影片是否推播完畢'''
    def check_ffmpy_process(self):
        if self.ffmpy_process is None:
            return
        try:
            if self.ffmpy_process.poll() is None:
                # log.debug("ffmpy_process alive!")
                # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                pass
            else:
                log.debug("poll() not None!")
                if self.play_status != play_status.stop:
                    self.play_status = play_status.stop
                    # self.ffmpy_process = None
                    # self.playing_file_name = None

        except Exception as e:
            log.debug(e)

    def check_play_status(self):

        if self.play_status != self.pre_play_status:
            # log.debug("self.play_status = %d", self.play_status )
            # log.debug("self.pre_play_status = %d", self.pre_play_status)
            self.signal_media_play_status_changed.emit(True, self.play_status)
            self.pre_play_status = self.play_status
            pass

    def set_brightness_level(self, level):
        self.video_params.set_video_brightness(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('brightness', self.video_params.get_translated_brightness())

    def set_contrast_level(self, level):
        self.video_params.set_video_contrast(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('contrast', self.video_params.get_translated_contrast())

    def set_red_bias_level(self, level):
        self.video_params.set_video_red_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('red_gain', self.video_params.get_translated_redgain())

    def set_green_bias_level(self, level):
        self.video_params.set_video_green_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('green_gain', self.video_params.get_translated_greengain())

    def set_blue_bias_level(self, level):
        self.video_params.set_video_blue_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('blue_gain', self.video_params.get_translated_bluegain())

    def set_sleep_mode(self, enable_or_disable):
        self.video_params.set_sleep_mode(enable_or_disable)

    def set_sleep_mode_enable(self):
        log.debug("set_sleep_mode_enable")
        self.video_params.set_sleep_mode(1)

    def set_sleep_mode_disable(self):
        log.debug("set_sleep_mode_disable")
        self.video_params.set_sleep_mode(0)

    def set_image_period_value(self, value):
        log.debug("value type: %s", type(value))
        log.debug("value : %d", value)
        self.video_params.set_image_peroid(value)

    def set_frame_brightness_value(self, value):
        self.video_params.set_frame_brightness(value)

    def set_day_mode_frame_brightness_value(self, value):
        self.video_params.set_day_mode_frame_brightness(value)

    def set_night_mode_frame_brightness_value(self, value):
        self.video_params.set_night_mode_frame_brightness(value)

    def set_sleep_mode_frame_brightness_value(self, value):
        self.video_params.set_sleep_mode_frame_brightness(value)

    def set_frame_br_divisor_value(self, value):
        self.video_params.set_frame_br_divisor(value)

    def set_frame_contrast_value(self, value):
        self.video_params.set_frame_contrast(value)

    def set_frame_gamma_value(self, value):
        self.video_params.set_frame_gamma(value)

    def set_crop_start_x_value(self, value):

        self.video_params.set_crop_start_x(value)

    def set_crop_start_y_value(self, value):
        self.video_params.set_crop_start_y(value)

    def set_crop_w_value(self, value):
        self.video_params.set_crop_w(value)

    def set_crop_h_value(self, value):
        self.video_params.set_crop_h(value)

    def set_hdmi_in_crop_start_x_value(self, value):
        self.video_params.set_hdmi_in_crop_start_x(value)

    def set_hdmi_in_crop_start_y_value(self, value):
        self.video_params.set_hdmi_in_crop_start_y(value)

    def set_hdmi_in_crop_w_value(self, value):
        self.video_params.set_hdmi_in_crop_w(value)

    def set_hdmi_in_crop_h_value(self, value):
        self.video_params.set_hdmi_in_crop_h(value)

    class play_playlist_work(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self, QObject, plist, n):
            super().__init__()
            self.media_processor = QObject
            self.playlist = plist
            self.n = n
            self.force_stop = False
            self.worker_status = 0
            self.file_idx = 0

        def run(self):
            log.debug("self.media_processor.repeat_option : %d", self.media_processor.repeat_option)
            self.media_processor.play_type = play_type.play_playlist
            self.file_idx = 0
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            if self.media_processor.play_status == play_status.pausing:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                        os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                        try:
                            os.popen("pkill ffplay")
                        except Exception as e:
                            log.debug(e)
                        # time.sleep(1)
                        log.debug("kill")
                    except Exception as e:
                        log.debug(e)
                if self.media_processor.repeat_option == repeat_option.repeat_random:
                    self.file_idx = random.randint(0, len(self.playlist.fileslist) - 1)
                log.debug("file_idx = %d", self.file_idx)
                self.file_uri = self.playlist.fileslist[self.file_idx]
                if os.path.exists(self.file_uri) is False:
                    self.file_idx += 1
                    if self.file_idx >= len(self.playlist.fileslist):
                        if self.media_processor.repeat_option != repeat_option.repeat_one:
                            log.debug("Quit Play Playlist")
                            break
                        else:
                            self.file_idx = 0
                    continue

                log.debug("self.file_uri = %s", self.file_uri)
                '''self.media_processor.ffmpy_process = \
                    neo_ffmpy_execute(self.file_uri,
                                      self.media_processor.video_params.get_translated_brightness(),
                                      self.media_processor.video_params.get_translated_contrast(),
                                      self.media_processor.video_params.get_translated_redgain(),
                                      self.media_processor.video_params.get_translated_greengain(),
                                      self.media_processor.video_params.get_translated_bluegain(),
                                      self.media_processor.video_params.image_period,
                                      self.media_processor.output_width,
                                      self.media_processor.output_height)'''
                ffmpeg_cmd = \
                    neo_ffmpy_execute(self.file_uri,
                                      self.media_processor.video_params.get_translated_brightness(),
                                      self.media_processor.video_params.get_translated_contrast(),
                                      self.media_processor.video_params.get_translated_redgain(),
                                      self.media_processor.video_params.get_translated_greengain(),
                                      self.media_processor.video_params.get_translated_bluegain(),
                                      self.media_processor.video_params.image_period,
                                      self.media_processor.output_width,
                                      self.media_processor.output_height)
                self.media_processor.ffmpy_process = subprocess.Popen(ffmpeg_cmd, shell=True)

                if self.media_processor.ffmpy_process.pid > 0:
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.file_uri
                    while True:
                        # if self.media_processor.play_status == play_status.stop:
                        #    break
                        if self.force_stop is True:
                            log.debug("self.force_stop is True A!")
                            if self.media_processor.ffmpy_process is not None:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                                try:
                                    os.popen("pkill ffplay")
                                except Exception as e:
                                    log.debug(e)
                                time.sleep(1)
                            break
                        # time.sleep(0.5)
                        # ffmpy exception
                        try:
                            res, err = self.media_processor.ffmpy_process.communicate()
                            log.debug("%s %s", res, err)
                            os.kill(self.media_processor.ffmpy_process.pid, 0)
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                        except OSError:
                            log.debug("no such process")
                            time.sleep(2)
                            break
                        else:
                            log.debug("ffmpy_process is still running")
                            time.sleep(1)
                            pass

                if self.force_stop is True:
                    log.debug("force_stop second")
                    break
                self.file_idx += 1
                if self.file_idx >= len(self.playlist.fileslist):
                    self.file_idx = 0
                    if self.media_processor.repeat_option == repeat_option.repeat_all or self.media_processor.repeat_option == repeat_option.repeat_random:
                        pass
                    else:
                        log.debug("self.media_processor.repeat_option : %d", self.media_processor.repeat_option)
                        log.debug("Quit Play Playlist After all file done")
                        break
                else:
                    pass
            self.finished.emit()
            self.worker_status = 0
            self.media_processor.play_type = play_type.play_none

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status

    class play_single_file_work(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self, QObject, file_uri, n):
            super().__init__()
            self.media_processor = QObject
            self.file_uri = file_uri
            self.n = n
            self.force_stop = False
            self.worker_status = 0
            self.force_stop_mutex = QMutex()

        def run(self):
            self.media_processor.play_type = play_type.play_single
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            if self.media_processor.play_status == play_status.pausing:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                        if self.media_processor.ffmpy_process is not None:
                            os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                            # time.sleep(1)
                            log.debug("kill")
                    except Exception as e:
                        log.debug(e)

                # log.debug("self.media_processor.video_params.image_period : %d",
                # self.media_processor.video_params.image_period)
                '''self.media_processor.ffmpy_process = \
                    neo_ffmpy_execute(self.file_uri,
                       self.media_processor.video_params.get_translated_brightness(),
                       self.media_processor.video_params.get_translated_contrast(),
                       self.media_processor.video_params.get_translated_redgain(),
                       self.media_processor.video_params.get_translated_greengain(),
                       self.media_processor.video_params.get_translated_bluegain(),
                       self.media_processor.video_params.image_period,
                       self.media_processor.output_width,
                       self.media_processor.output_height)'''
                ffmpeg_cmd = \
                       neo_ffmpy_execute(self.file_uri,
                       self.media_processor.video_params.get_translated_brightness(),
                       self.media_processor.video_params.get_translated_contrast(),
                       self.media_processor.video_params.get_translated_redgain(),
                       self.media_processor.video_params.get_translated_greengain(),
                       self.media_processor.video_params.get_translated_bluegain(),
                       self.media_processor.video_params.image_period,
                       self.media_processor.output_width,
                       self.media_processor.output_height)
                # log.debug("AAAAAAAAAAAAAAAAAAAAAAAA")
                self.media_processor.ffmpy_process = subprocess.Popen(ffmpeg_cmd, shell=True)
                # log.debug("BBBBBBBBBBBBBBBBBBBBBBBBB")
                log.debug("self.media_processor.ffmpy_process.pid = %d", self.media_processor.ffmpy_process.pid)
                if self.media_processor.ffmpy_process.pid > 0:
                    log.debug("self.media_processor.ffmpy_process.pid = %d", self.media_processor.ffmpy_process.pid)
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.file_uri
                    while True:

                        # if self.media_processor.play_status == play_status.stop:
                        #    break
                        if self.force_stop is True:
                            log.debug("self.force_stop is True A!")
                            if self.media_processor.ffmpy_process is not None:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                                try:
                                    os.popen("pkill ffplay")
                                except Exception as e:
                                    log.debug(e)
                                time.sleep(1)
                            break
                        # time.sleep(0.5)
                        # ffmpy exception 
                        try:
                            res, err = self.media_processor.ffmpy_process.communicate()
                            log.debug("%s %s", res, err)
                            os.kill(self.media_processor.ffmpy_process.pid, 0)
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                        except OSError:
                            log.debug("no such process")
                            try:
                                os.popen("pkill ffplay")
                            except Exception as e:
                                log.debug(e)
                            # time.sleep(2)
                            break
                        else:
                            log.debug("ffmpy_process is still running")
                            # time.sleep(1)
                            pass

                if self.media_processor.repeat_option == repeat_option.repeat_none:
                    log.debug("stop play cause play end")
                    break
                if self.force_stop is True:
                    log.debug("self.force_stop is True B!")
                    break
                # self.force_stop_mutex.unlock()
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                while True:
                    if len(os.popen("pgrep -f h264_v4l2m2m").read()) != 0:
                        os.popen("pkill -f h264_v4l2m2m")
                        try:
                            os.popen("pkill ffplay")
                        except Exception as e:
                            log.debug(e)
                        log.debug("still have ffmpeg v4l2m2m")
                    else:
                        log.debug("no ffmpeg v4l2m2m")
                        break
                    # time.sleep(1)
            # time.sleep(1)
            
            log.debug("play single file ready to quit")
            self.finished.emit()
            self.media_processor.play_status = play_status.stop
            self.media_processor.play_type = play_type.play_none
            self.worker_status = 0

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status

    class play_hdmi_in_work(QObject):
        signal_play_hdmi_in_finish = pyqtSignal()
        signal_play_hdmi_in_start = pyqtSignal()

        def __init__(self, QObject, video_src, cast_dst):
            super().__init__()
            self.media_processor = QObject
            self.video_src = video_src
            self.cast_dst = cast_dst
            #log.debug("cast_dst :%s", cast_dst)
            self.force_stop = False
            self.worker_status = 0

        def run(self):
            self.media_processor.play_type = play_type.play_hdmi_in
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    ''' kill other streaming ffmpy instance first'''
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            try:
                                if self.media_processor.play_status == play_status.pausing:
                                    os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                            except Exception as e:
                                log.debug(e)
                        if self.media_processor.ffmpy_process is not None:
                            os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                            # time.sleep(1)
                            log.debug("kill")
                    except Exception as e:
                        log.debug(e)

                '''self.media_processor.ffmpy_process = \
                    neo_ffmpy_cast_video_h264(self.video_src, self.cast_dst, 
                       self.media_processor.video_params.get_translated_brightness(),
                       self.media_processor.video_params.get_translated_contrast(),
                       self.media_processor.video_params.get_translated_redgain(),
                       self.media_processor.video_params.get_translated_greengain(),
                       self.media_processor.video_params.get_translated_bluegain(),
                       self.media_processor.output_width,
                       self.media_processor.output_height)'''
                ffmpeg_cmd = \
                    neo_ffmpy_cast_video_h264(self.video_src, self.cast_dst,
                                              self.media_processor.video_params.get_translated_brightness(),
                                              self.media_processor.video_params.get_translated_contrast(),
                                              self.media_processor.video_params.get_translated_redgain(),
                                              self.media_processor.video_params.get_translated_greengain(),
                                              self.media_processor.video_params.get_translated_bluegain(),
                                              self.media_processor.output_width,
                                              self.media_processor.output_height)

                self.media_processor.ffmpy_process = subprocess.Popen(ffmpeg_cmd, shell=True)
                self.media_processor.hdmi_in_audio_process = subprocess.Popen("play_hdmi_in_audio.sh", shell=True)
                if self.media_processor.ffmpy_process is None:
                    continue

                log.debug("self.media_processor.ffmpy_process.pid = %d", self.media_processor.ffmpy_process.pid)

                if self.media_processor.ffmpy_process.pid > 0:
                    self.signal_play_hdmi_in_start.emit()
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.video_src
                    while True:
                        # if self.media_processor.play_status == play_status.stop:
                        #    break
                        if self.force_stop is True:
                            log.debug("self.force_stop is True A!")
                            if self.media_processor.ffmpy_process is not None:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                                time.sleep(1)
                            break
                        # time.sleep(0.5)
                        # ffmpy exception
                        try:
                            res, err = self.media_processor.ffmpy_process.communicate()
                            log.debug("%s %s", res, err)
                            os.kill(self.media_processor.ffmpy_process.pid, 0)
                        except OSError:
                            log.debug("no such process")
                            time.sleep(2)
                            break
                        else:
                            log.debug("ffmpy_process is still running")
                            time.sleep(1)
                            pass

                if self.force_stop is True:
                    os.popen("pkill -f play_hdmi_in_audio.sh")
                    os.popen("pkill -f arecord")
                    os.popen("pkill -f aplay")
                    break
            log.debug("play hdmi-in ready to quit")

            self.signal_play_hdmi_in_finish.emit()
            self.media_processor.play_type = play_type.play_none
            self.worker_status = 0

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status

    class play_cms_work(QObject):
        signal_play_cms_finish = pyqtSignal()
        signal_play_cms_start = pyqtSignal()

        def __init__(self, QObject, window_width, window_height, window_x, window_y, cast_dst):
            super().__init__()
            self.media_processor = QObject
            self.window_width = window_width
            self.window_height = window_height
            self.window_x = window_x
            self.window_y = window_y
            self.cast_dst = cast_dst
            self.video_src = ":0.0+" + str(window_x) + "," + str(window_y)
            #log.debug("cast_dst :%s", cast_dst)
            self.force_stop = False
            self.worker_status = 0

        def run(self):
            self.media_processor.play_type = play_type.play_cms
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    ''' kill other streaming ffmpy instance first'''
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            try:
                                if self.media_processor.play_status == play_status.pausing:
                                    os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                            except Exception as e:
                                log.debug(e)
                        if self.media_processor.ffmpy_process is not None:
                            os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                            # time.sleep(1)
                            log.debug("kill")
                    except Exception as e:
                        log.debug(e)

                '''self.media_processor.ffmpy_process = \
                    neo_ffmpy_cast_cms(self.video_src, self.cast_dst,
                                       self.window_width, self.window_height, self.window_x, self.window_y,
                                       self.media_processor.video_params.get_translated_brightness(),
                                       self.media_processor.video_params.get_translated_contrast(),
                                       self.media_processor.video_params.get_translated_redgain(),
                                       self.media_processor.video_params.get_translated_greengain(),
                                       self.media_processor.video_params.get_translated_bluegain(),
                                       self.media_processor.output_width,
                                       self.media_processor.output_height)'''
                ffmpeg_cmd = \
                    neo_ffmpy_cast_cms(self.video_src, self.cast_dst,
                                       self.window_width, self.window_height, self.window_x, self.window_y,
                                       self.media_processor.video_params.get_translated_brightness(),
                                       self.media_processor.video_params.get_translated_contrast(),
                                       self.media_processor.video_params.get_translated_redgain(),
                                       self.media_processor.video_params.get_translated_greengain(),
                                       self.media_processor.video_params.get_translated_bluegain(),
                                       self.media_processor.output_width,
                                       self.media_processor.output_height)
                self.media_processor.ffmpy_process = subprocess.Popen(ffmpeg_cmd, shell=True)

                if self.media_processor.ffmpy_process is not None:
                    self.signal_play_cms_start.emit()
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = "CMS"
                    while True:
                        # if self.media_processor.play_status == play_status.stop:
                        #    break
                        if self.force_stop is True:
                            log.debug("self.force_stop is True A!")
                            if self.media_processor.ffmpy_process is not None:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGTERM)
                                time.sleep(1)
                            break
                        # time.sleep(0.5)
                        # ffmpy exception
                        try:
                            res, err = self.media_processor.ffmpy_process.communicate()
                            log.debug("%s %s", res, err)
                            os.kill(self.media_processor.ffmpy_process.pid, 0)
                        except OSError:
                            log.debug("no such process")
                            time.sleep(2)
                            break
                        else:
                            log.debug("ffmpy_process is still running")
                            time.sleep(1)
                            pass

                if self.force_stop is True:
                    break

            self.signal_play_cms_finish.emit()
            self.media_processor.play_type = play_type.play_none
            self.worker_status = 0

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status


