import ffmpy
from time import sleep
import threading
from global_def import *
import platform
import utils.log_utils
log = utils.log_utils.logging_init('ffmpy_utils')

def ffmpy_execute(QObject, video_path):
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        ff = ffmpy.FFmpeg(
            inputs={video_path: ["-re"]},
            outputs={udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", "-f", "h264", "-localaddr", "192.168.0.3"]}
            #outputs={udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", "-f", "h264"]}
            # outputs={udp_sink: ["-vcodec", "copy", "-f", "h264"]}
        )
    else:
        ff = ffmpy.FFmpeg(
            inputs={video_path: ["-re"]},
            #outputs={udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", "-f", "h264", "-localaddr", "192.168.0.3"]}
            outputs={udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", "-f", "h264"]}
            # outputs={udp_sink: ["-vcodec", "copy", "-f", "h264"]}
        )

    log.debug("%s", ff.cmd)
    try:
        thread_1 = threading.Thread(target=ff.run)
        thread_1.start()
        while not ff.process:
            sleep(0.05)
    except RuntimeError as e:
        log.error(e)

    mainUI = QObject
    mainUI.ffmpy_running = play_status.playing
    mainUI.ff_process = ff.process
    log.debug("ffmpy_running : %d", mainUI.ffmpy_running)
    log.debug("ff.process : %s", ff.process)
    log.debug("ff.process pid : %d", ff.process.pid)

    return ff.process

def ffmpy_execute_list(QObject, video_path_list):
    mainUI = QObject

    while True:
        for videoparam in video_path_list:
            try:
                """ No ff_process"""
                if mainUI.ff_process is None:
                    mainUI.ffmpy_running = play_status.stop
                else:
                    """ a ff_process is running , wait process done"""
                    while True:
                        sleep(2)
                        if mainUI.play_type == play_type.play_none:
                            return
                        if mainUI.ff_process.poll() is not None:
                            mainUI.ffmpy_running = play_status.stop
                            break


                if mainUI.ffmpy_running == play_status.stop:
                    log.debug("playing %s", videoparam.file_uri)
                    video_path = videoparam.file_uri
                    thread_1 = threading.Thread(target=ffmpy_execute, args=(QObject, video_path,))
                    thread_1.start()
                    sleep(2)
                #else:
                #    while True:
                #        if mainUI.ff_process.poll() is None:
                #            break;


            except RuntimeError as e:
                log.error(e)

        if mainUI.play_option_repeat != repeat_option.repeat_all:
            log.debug("No Repeat All")
            break

        if mainUI.play_type == play_type.play_none:
            return


