import ffmpy
from time import sleep
import threading
from global_def import *
import platform
import os
import utils.log_utils
log = utils.log_utils.logging_init('ffmpy_utils')

def ffmpy_execute(QObject, video_path, width=80, height=96):
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)
    eq_params = "eq=brightness=0.0"
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                        video_path: ["-re"]
                    },
            outputs={
                        udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', scale_params, "-f", "h264", "-localaddr", "192.168.0.3"]
                     },

        )
    else:
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={video_path: ["-re"]},
            outputs={
                #udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', eq_params,  "-f",
                #           "h264", "-localaddr", "192.168.0.2"]}
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', scale_params, '-vf', eq_params , "-f", "h264", "-localaddr", "192.168.0.2"]}

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


def gen_webp_from_video(file_folder, video):

    thumbnail_path = internal_media_folder + ThumbnailFileFolder + video.replace(".mp4", ".webp")
    video_path = file_folder + "/" + video
    thunbnail_folder_path = internal_media_folder + ThumbnailFileFolder
    if not os.path.exists(thunbnail_folder_path):
        os.makedirs(thunbnail_folder_path)

    if os.path.isfile(thumbnail_path) is False:
        global_opts = '-hide_banner -loglevel error'
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={video_path: ['-ss', '3', '-t', '3']},
            outputs={thumbnail_path: ['-vf', 'scale=640:480']}
        )
        ff.run()
    return thumbnail_path
