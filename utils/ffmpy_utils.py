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

still_image_loop_cnt = 1
still_image_video_period = 600
preview_start_time = 3
preview_period = 3

def neo_ffmpy_execute(video_path, brightness, contrast, red_bias, green_bias, blue_bias,
                      width=80, height=96):
    ff = None
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)  # + ",hflip"
    brightness_params = "brightness=" + str(brightness)
    contrast_params = "contrast=" + str(contrast)
    eq_str = "eq=" + brightness_params + ":" + contrast_params
    red_bias_params = "romin=" + str(red_bias)
    green_bias_params = "gomin=" + str(green_bias)
    blue_bias_params = "bomin=" + str(blue_bias)
    crop_str = "crop=iw:ih:0:0"

    color_level_str = "colorlevels=" + red_bias_params + ":" + green_bias_params + ":" + blue_bias_params

    # add TEXT
    if "blank" in video_path:
        drawtext_str = "drawtext=fontfile=" + internal_media_folder + \
                      "/fonts/msjhbd.ttc:text='歡迎長虹光電蒞臨指導':x=10*w/80-40*t:y=20:fontsize=72*h/96:fontcolor=white"
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + drawtext_str + "," + scale_params
    else:
        drawtext_str = "drawtext=fontfile=" + internal_media_folder + \
                       "/fonts/msjhbd.ttc:text='':x=10:y=20:fontsize=24*h/96:fontcolor=black"
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + drawtext_str + "," + crop_str + "," + scale_params

    video_encoder = "libx264"

    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        if width > 320 and height > 240:
            video_encoder = "h264_v4l2m2m"
        else:
            video_encoder = "libx264"
        if video_path.endswith("mp4"):
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={
                    video_path: ["-re"]
                },
                outputs={
                    udp_sink: ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                               "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.3"]
                },
            )
        elif video_path.endswith("jpeg") or video_path.endswith("jpg") or video_path.endswith("png"):
            log.debug("jpg to mp4")
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={
                    video_path: ["-loop", str(still_image_loop_cnt), "-t", str(still_image_video_period), "-re"]
                },
                outputs={
                    udp_sink: ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                               "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.3"]

                },
            )
        elif video_path.startswith("udp"):
            log.debug("udp to mp4")
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={
                    video_path: ["-f", "h264", ]
                },
                outputs={
                    udp_sink: ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                               "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]

                },
            )
    else:
        if video_path.endswith("mp4"):
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={video_path: ["-re"]},

                outputs={
                    udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-filter_complex', filter_params,
                               "-g", "60", "-f", "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"],
                    #udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-filter_complex', filter_params,
                    #           "-g", "120", "-f", "h264", "-localaddr", "192.168.0.2"],
                }
            )
        elif video_path.endswith("jpeg") or video_path.endswith("jpg") or video_path.endswith("png"):
            log.debug("jpg to mp4")
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={
                    video_path: ["-loop", str(still_image_loop_cnt), "-t", str(still_image_video_period), "-re"]
                },
                outputs={
                    udp_sink: ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                                "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]

                },
            )
        elif video_path.startswith("udp"):
            log.debug("udp to mp4")
            ff = ffmpy.FFmpeg(
                global_options=global_opts,
                inputs={
                    video_path: ["-f", "h264", ]
                },
                outputs={
                    udp_sink: ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                               "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]

                },
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

def neo_ffmpy_execute_hdmi_in(video_path, video_dst,brightness, contrast, red_bias, green_bias, blue_bias,
                      width=80, height=96):
    ff = None
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)  # + ",hflip"
    brightness_params = "brightness=" + str(brightness)
    contrast_params = "contrast=" + str(contrast)
    eq_str = "eq=" + brightness_params + ":" + contrast_params
    red_bias_params = "romin=" + str(red_bias)
    green_bias_params = "gomin=" + str(green_bias)
    blue_bias_params = "bomin=" + str(blue_bias)
    crop_str = "crop=iw:ih:0:0"

    color_level_str = "colorlevels=" + red_bias_params + ":" + green_bias_params + ":" + blue_bias_params

    # add TEXT
    if "blank" in video_path:
        drawtext_str = "drawtext=fontfile=" + internal_media_folder + \
                      "/fonts/msjhbd.ttc:text='歡迎長虹光電蒞臨指導':x=10*w/80-40*t:y=20:fontsize=72*h/96:fontcolor=white"
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + drawtext_str + "," + scale_params
    else:
        drawtext_str = "drawtext=fontfile=" + internal_media_folder + \
                       "/fonts/msjhbd.ttc:text='':x=10:y=20:fontsize=24*h/96:fontcolor=black"
        filter_params = "zmq," + eq_str + "," + color_level_str + "," + drawtext_str + "," + crop_str + "," + scale_params

    video_encoder = "libx264"

    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        if width > 320 and height > 240:
            video_encoder = "h264_v4l2m2m"
        else:
            video_encoder = "libx264"
        video_encoder = "libx264"
        output = {}
        input_res = str(width) + "x" + str(height)
        '''handle udp streaming'''
        for i in video_dst:
            if i == cv2_preview_h264_sink:
                output[i] = ["-vcodec", video_encoder, "-f", "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]
            else:
                output[i] = ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                             "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                video_path: ["-f", "v4l2", "-pix_fmt", "mjpeg", "-s", input_res]
            },
            outputs=output,
        )
    else:
        video_encoder = "libx264"
        output = {}
        input_res = str(width) + "x" + str(height)
        '''handle udp streaming'''
        for i in video_dst:
            if i == cv2_preview_h264_sink:
                output[i] = ["-vcodec", video_encoder, "-f", "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]
            else:
                output[i] = ["-vcodec", video_encoder, '-filter_complex', filter_params, "-b:v", "2000k", "-f",
                           "h264", "-pix_fmt", "yuv420p", "-localaddr", "192.168.0.2"]
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                video_path: ["-f", "v4l2", "-pix_fmt", "mjpeg", "-s", input_res]
            },
            outputs=output,
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

def neo_ffmpy_cast_video_v4l2(video_path, cast_dst, brightness, contrast, red_bias, green_bias, blue_bias, width=80, height=96):
    if len(cast_dst) == 0 or cast_dst is None:
        return -1
    ff = None
    global_opts = '-hide_banner -loglevel error'
    output = {}

    for i in cast_dst:
        output[i] = ["-f", "v4l2", "-c:v", "copy"]

    ff = ffmpy.FFmpeg(
        global_options=global_opts,
        inputs={
            video_path: ["-f", "v4l2", "-input_format", "mjpeg", "-s", "640x480", "-framerate", "30"]
        },
        outputs=output,
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
    try:
        os.kill(ff.process.pid, 0)
    except:
        log.debug("ffmpy_hdmi_in_cast_process is gone")
        ff.process = None
    else:
        log.debug("ffmpy_hdmi_in_cast_process is alive")
    return ff.process

def neo_ffmpy_cast_video_h264(video_path, cast_dst, brightness, contrast, red_bias, green_bias, blue_bias, width=80, height=96):
    if len(cast_dst) == 0 or cast_dst is None:
        return -1
    ff = None
    global_opts = '-hide_banner -loglevel error'
    out_res = str(width) + "x" + str(height)
    output = {}
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        if width >= 320 and height >= 240:
            video_encoder = "h264_v4l2m2m"
        else:
            video_encoder = "libx264"
    else:
        video_encoder = "libx264"
    for i in cast_dst:
        output[i] = ["-vcodec", video_encoder, "-pix_fmt", "yuv420p","-b:v", "200k", "-s", out_res, "-f", "h264", "-localaddr", "192.168.0.3"]

    ff = ffmpy.FFmpeg(
        global_options=global_opts,
        inputs={
            video_path: ["-f", "v4l2", "-pix_fmt", "mjpeg", "-s", out_res, "-framerate", "30"]
        },
        outputs=output,
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
    try:
        os.kill(ff.process.pid, 0)
    except:
        log.debug("ffmpy_hdmi_in_cast_process is gone")
        ff.process = None
    else:
        log.debug("ffmpy_hdmi_in_cast_process is alive")
    return ff.process


def neo_ffmpy_cast_video_depreciated(video_path, cast_dst_0, cast_dst_1, width=80, height=96):

    ff = None
    global_opts = '-hide_banner -loglevel error'
    ff = ffmpy.FFmpeg(
        global_options=global_opts,
        inputs={
            video_path: ["-f", "v4l2", "-input_format", "mjpeg", "-s", "640x480", "-framerate", "30"]
        },
        outputs={
            cast_dst_0: ["-f", "v4l2", "-c", "copy"],
            cast_dst_1: ["-f", "v4l2", "-c", "copy"]
        },
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


# deprecated
'''def ffmpy_execute(QObject, video_path, width=80, height=96):
    global_opts = '-hide_banner -loglevel error'
    scale_params = "scale=" + str(width) + ":" + str(height)
    eq_params = "zmq,eq=brightness=0.0" + "," + scale_params

    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={
                video_path: ["-re"]
            },
            outputs={
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '--filter_complex', eq_params, "-f", "h264",
                           "-localaddr", "192.168.0.3"]
                # udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-vf', scale_params, "-f", "h264",
                #           "-localaddr", "192.168.0.3"]
            },

        )
    else:
        ff = ffmpy.FFmpeg(
            global_options=global_opts,
            inputs={video_path: ["-re"]},
            outputs={
                udp_sink: ["-preset", "ultrafast", "-vcodec", "libx264", '-filter_complex', eq_params, "-f", "h264",
                           "-localaddr", "192.168.0.2"]
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

    return ff.process'''


# deprecated
'''def ffmpy_execute_list(QObject, video_path_list):
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
                # else:
                #    while True:
                #        if mainUI.ff_process.poll() is None:
                #            break;


            except RuntimeError as e:
                log.error(e)

        if mainUI.play_option_repeat != repeat_option.repeat_all:
            log.debug("No Repeat All")
            break

        if mainUI.play_type == play_type.play_none:
            return'''


def gen_webp_from_video(file_folder, video):
    # use hashlib md5 to generate preview file name
    video_name = video.split(".")[0]
    video_extension = video.split(".")[1]
    log.debug("video_extension = %s", video_extension)
    preview_file_name = hashlib.md5(video_name.encode('utf-8')).hexdigest()

    # thumbnail_path = internal_media_folder + ThumbnailFileFolder + video.replace(".mp4", ".webp")
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
            if video_extension in ["jpeg", "jpg", "png"]:
                log.debug("still image")
                ff = ffmpy.FFmpeg(
                    global_options=global_opts,
                    inputs={video_path: ['-loop', str(still_image_loop_cnt), '-t', str(preview_period)]},
                    outputs={thumbnail_path: ['-vf', 'scale=640:480']}
                )
            else:
                ff = ffmpy.FFmpeg(
                    global_options=global_opts,
                    inputs={video_path: ['-ss', str(preview_start_time), '-t', str(preview_period)]},
                    outputs={thumbnail_path: ['-vf', 'scale=640:480']}
                )
            log.debug("%s", ff.cmd)
            ff.run()
    except Exception as e:
        log.debug(e)
    return thumbnail_path

def gen_webp_from_video_threading(file_folder, video):
    threads = []
    threads.append(threading.Thread(target=gen_webp_from_video, args=(file_folder, video,)))
    threads[0].start()

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


def ffmpy_draw_text(text):
    context = zmq.Context()
    log.debug("Connecting to server...")
    cmd = "Parsed_drawtext_3 reinit text=" + str(text)
    log.debug("cmd : %s", cmd)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    log.debug("cmd : %s", cmd)
    socket.send(cmd.encode())

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()

def ffmpy_crop_enable(crop_x, crop_y, crop_w, crop_h, led_w, led_h):
    context = zmq.Context()
    log.debug("Connecting to server...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    socket.send(("Parsed_crop_4 w " + str(crop_w)).encode())
    data = socket.recv(1024)
    log.debug("recv data = %s", data.decode())
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        log.debug("Error")
        return False
    socket.send(("Parsed_crop_4 h " + str(crop_h)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False
    socket.send(("Parsed_crop_4 x " + str(crop_x)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False
    socket.send(("Parsed_crop_4 y " + str(crop_y)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False
    socket.send(("Parsed_scale_5 w " + str(led_w)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False
    socket.send(("Parsed_scale_5 h " + str(led_h)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False
    socket.disconnect("tcp://localhost:%s" % 5555)
    context.destroy()
    context.term()
    log.debug("set scale end")
    return True

def ffmpy_crop_disable(led_w, led_h):
    context = zmq.Context()
    log.debug("Connecting to server...")

    cmd_w = "Parsed_crop_4 w iw"
    cmd_h = "Parsed_crop_4 h ih"
    cmd_x = "Parsed_crop_4 x 0"
    cmd_y = "Parsed_crop_4 y 0"
    cmd_scale_w = "Parsed_scale_5 w " + str(led_w)
    cmd_scale_h = "Parsed_scale_5 h " + str(led_h)
    log.debug("cmd_w : %s", cmd_w)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    socket.send(("Parsed_crop_4 w iw" ).encode())
    data = socket.recv(1024)
    log.debug("recv data = %s", data.decode())
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        log.debug("Error")
        return False

    socket.send(("Parsed_crop_4 h ih").encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False

    socket.send(("Parsed_crop_4 x 0").encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False

    socket.send(("Parsed_crop_4 y 0").encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False

    socket.send(("Parsed_scale_5 w " + str(led_w)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False

    socket.send(("Parsed_scale_5 h " + str(led_h)).encode())
    data = socket.recv(1024)
    if 'Success' not in data.decode():
        socket.disconnect("tcp://localhost:%s" % 5555)
        context.destroy()
        context.term()
        return False

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()

def ffmpy_crop_enable_depreciated(crop_x, crop_y, crop_w, crop_h, led_w, led_h):
    context = zmq.Context()
    log.debug("Connecting to server...")

    cmd_w = "Parsed_crop_4 w " + str(crop_w)
    cmd_h = "Parsed_crop_4 h " + str(crop_h)
    cmd_x = "Parsed_crop_4 x " + str(crop_x)
    cmd_y = "Parsed_crop_4 y " + str(crop_y)
    cmd_scale_w = "Parsed_scale_5 w " + str(led_w)
    cmd_scale_h = "Parsed_scale_5 h " + str(led_h)
    log.debug("cmd_w : %s", cmd_w)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    socket.send(cmd_w.encode())
    data = socket.recv(1024)

    socket.send(cmd_h.encode())
    data = socket.recv(1024)
    # log.debug("data = %s", data)
    socket.send(cmd_x.encode())
    data = socket.recv(1024)
    # log.debug("data = %s", data)
    socket.send(cmd_y.encode())
    data = socket.recv(1024)
    # log.debug("data = %s", data)

    socket.send(cmd_scale_w.encode())
    data = socket.recv(1024)
    # log.debug("data = %s", data)

    socket.send(cmd_scale_h.encode())
    data = socket.recv(1024)
    # log.debug("data = %s", data)

    socket.disconnect("tcp://localhost:%s" % 5555)

    context.destroy()
    context.term()

def ffmpy_crop_disable_depreciated(led_w, led_h):
    context = zmq.Context()
    log.debug("Connecting to server...")

    cmd_w = "Parsed_crop_4 w iw"
    cmd_h = "Parsed_crop_4 h ih"
    cmd_x = "Parsed_crop_4 x 0"
    cmd_y = "Parsed_crop_4 y 0"
    cmd_scale_w = "Parsed_scale_5 w " + str(led_w)
    cmd_scale_h = "Parsed_scale_5 h " + str(led_h)
    log.debug("cmd_w : %s", cmd_w)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % 5555)

    socket.send(cmd_w.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)
    socket.send(cmd_h.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)
    socket.send(cmd_x.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)
    socket.send(cmd_y.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)

    socket.send(cmd_scale_w.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)

    socket.send(cmd_scale_h.encode())
    data = socket.recv(1024)
    log.debug("data = %s", data)

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
