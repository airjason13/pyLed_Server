import ffmpy
from time import sleep
import threading
from global_def import *
import platform
import os
import zmq
import utils.log_utils
import hashlib
log = utils.log_utils.logging_init('ffmpy_utils')

def neo_ffmpy_execute( video_path, brightness, contrast, red_bias, green_bias, blue_bias, width=80, height=96):
    # red_bias = 0.9
    # green_bias = 0.9
    # blue_bias = 0.9
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)  #+ ",hflip"
    brightness_params = "brightness=" + str(brightness)
    # brightness_params = "brightness=" + str(-0.9)
    contrast_params = "contrast=" + str(contrast)
    # contrast_params = "contrast=" + str(100)
    eq_str = "eq=" + brightness_params + ":" + contrast_params
    red_bias_params = "romin=" + str(red_bias)
    green_bias_params = "gomin=" + str(green_bias)
    blue_bias_params = "bomin=" + str(blue_bias)
    # filter2_str = "colorlevels=" + "rimin=0.99:gimin=0.99:bimin=0.99:" + red_bias_params + ":" + green_bias_params + ":" + blue_bias_params

    color_level_str = "colorlevels=" + red_bias_params + ":" + green_bias_params + ":" + blue_bias_params

    # add TEXT
    if "blank.mp4" in video_path:
        drawtext_str = "drawtext=fontfile=" + internal_media_folder + \
                       "/fonts/msjhbd.ttc:text='歡迎MIH蒞臨指導':x=10*w/80-80*t:y=0:fontsize=24*h/96:fontcolor=white"
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + drawtext_str + "," + scale_params
    else:
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + scale_params


    video_encoder = "libx264"

    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        if width > 320 and height > 240:
            video_encoder = "h264_v4l2m2m"
        else:
            video_encoder = "libx264"

        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                        video_path: ["-re"]
                    },
            outputs={
                udp_sink: [ "-vcodec", video_encoder, '-filter_complex', filter_params,"-b:v", "2000k", "-f", "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.3"]
                #udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', scale_params, "-f", "h264", "-localaddr", "192.168.0.3"]
            },

        )
    else:
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={video_path: ["-re"]},

            outputs={
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-filter_complex', filter_params , "-f", "h264", "-localaddr", "192.168.0.2"],
            }
        )

    log.debug("%s", ff.cmd)
    try:
        thread_1 = threading.Thread(target=ff.run)
        thread_1.start()
        while not ff.process:
            sleep(0.05)
    except RuntimeError as e:
        log.error(e)

    log.debug("ff.process : %s", ff.process)
    log.debug("ff.process pid : %d", ff.process.pid)

    return ff.process

''' deprecated'''
def ffmpy_execute(QObject, video_path, width=80, height=96):
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)
    eq_params = "zmq,eq=brightness=0.0"+","+scale_params

    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                        video_path: ["-re"]
                    },
            outputs={
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '--filter_complex', eq_params,"-f", "h264", "-localaddr", "192.168.0.3"]
                #udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', scale_params, "-f", "h264",
                #           "-localaddr", "192.168.0.3"]
            },

        )
    else:
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={video_path: ["-re"]},
            outputs={
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-filter_complex', eq_params, "-f", "h264", "-localaddr", "192.168.0.2"]
            }
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

''' deprecated'''
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
    # use hashlib md5 to generate preview file name
    video_name = video.split(".")[0]
    preview_file_name = hashlib.md5(video_name.encode('utf-8')).hexdigest()

    #thumbnail_path = internal_media_folder + ThumbnailFileFolder + video.replace(".mp4", ".webp")
    thumbnail_path = internal_media_folder + ThumbnailFileFolder + preview_file_name + ".webp"
    video_path = file_folder + "/" + video
    log.debug("video_path = %s", video_path)
    log.debug("thumbnail_path = %s", thumbnail_path)
    thunbnail_folder_path = internal_media_folder + ThumbnailFileFolder
    if not os.path.exists(thunbnail_folder_path):
        os.makedirs(thunbnail_folder_path)
    try:
        if os.path.isfile(thumbnail_path) is False:
            global_opts = '-hide_banner -loglevel error'
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={video_path: ['-ss', '3', '-t', '3']},
                outputs={thumbnail_path: ['-vf', 'scale=640:480']}
            )
            ff.run()
    except Exception as e:
        log.debug(e)
    return thumbnail_path


def ffmpy_set_video_param_level(param_name, level):
    cmd = ""
    if param_name == 'brightness':
        cmd = "Parsed_eq_1 brightness " + str(level)
    elif param_name == 'contrast':
        cmd = "Parsed_eq_1 contrast " + str(level)
    elif param_name == 'red_gain':
        cmd = "Parsed_colorlevels_2 romin " + str(level)
    elif param_name == 'green_gain':
        cmd = "Parsed_colorlevels_2 gomin " + str(level)
    elif param_name == 'blue_gain':
        cmd = "Parsed_colorlevels_2 bomin " + str(level)

    if cmd == "":
        log.error("cmd is NULL")
        return
    context = zmq.Context()
    log.debug("Connecting to server...")

    log.debug("cmd : %s", cmd)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    log.debug("cmd : %s", cmd)
    socket.send(cmd.encode())

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()

'''def ffmpy_set_brightness_level(level):
    context = zmq.Context()
    log.debug("Connecting to server...")

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)
    cmd = "Parsed_eq_1 brightness " + str(level)
    log.debug("cmd : %s", cmd)
    socket.send(cmd.encode())

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()
    
def ffmpy_set_contrast_level(level):
    context = zmq.Context()
    log.debug("Connecting to server...")

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)
    cmd = "Parsed_eq_1 contrast " + str(level)
    log.debug("cmd : %s", cmd)
    socket.send(cmd.encode())

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()'''