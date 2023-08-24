import glob
import subprocess

import utils.log_utils
import os
import pyudev
import psutil
import pyinotify
from global_def import *
from subprocess import Popen, PIPE
from subprocess import check_output, CalledProcessError
import sys
from global_def import *


def get_media_file_list(dir, with_path=False):
    log.error("dir : %s", dir)
    file_list = glob.glob(dir + "/*.mp4") + glob.glob(dir + "/*.jpg") + glob.glob(dir + "/*.jpeg") + glob.glob(dir + "/*.png")

    return file_list


def get_playlist_file_list(dir, with_path=False):
    log.debug("dir : %s", dir)
    file_list = glob.glob(dir + "/*.playlist")
    print("type(file_list) = %s", type(file_list))
    return file_list


def get_mount_points(devices=None):
    context = pyudev.Context()

    mount_points = []
    # 分割磁區的pen drive
    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if
                 device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in
                      context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]

        for p in psutil.disk_partitions():
            if p.device in partitions:
                mount_points.append(p.mountpoint)

    # 未分割磁區的pen drive
    for device in removable:
        partitions = [device.device_node for device in
                      context.list_devices(subsystem='block', DEVTYPE='disk', parent=device)]

        for p in psutil.disk_partitions():
            if p.device in partitions:
                mount_points.append(p.mountpoint)
    return mount_points

def change_text_content(content):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_file_name, 'w')
    config_file.write(content)
    config_file.close()
    os.system("sync")

def change_text_size(size):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_size_file_name, 'w')
    config_file.write(size)
    config_file.close()
    os.system("sync")

def change_text_speed(speed):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_speed_file_name, 'w')
    config_file.write(speed)
    config_file.close()
    os.system("sync")

def change_text_position(speed):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_position_file_name, 'w')
    config_file.write(speed)
    config_file.close()
    os.system("sync")

def change_text_period(period):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_period_file_name, 'w')
    config_file.write(period)
    config_file.close()
    os.system("sync")


def get_text_size():
    if os.path.exists(internal_media_folder + SubtitleFolder) is False:
        os.mkdir(internal_media_folder + SubtitleFolder)
    if os.path.exists(internal_media_folder + SubtitleFolder + subtitle_size_file_name) is False:
        text_font_size = str(text_font_size_default)
        text_font_size_config_file = open(internal_media_folder + SubtitleFolder + subtitle_size_file_name, 'w')
        text_font_size_config_file.write(text_font_size)
        text_font_size_config_file.close()
        return text_font_size
    else:
        text_font_size_config_file = open(internal_media_folder + SubtitleFolder + subtitle_size_file_name, 'r')
        text_font_size = text_font_size_config_file.readline()
        text_font_size_config_file.close()
    return text_font_size


def get_text_speed():
    if os.path.exists(internal_media_folder + SubtitleFolder) is False:
        os.mkdir(internal_media_folder + SubtitleFolder)
    if os.path.exists(internal_media_folder + SubtitleFolder + subtitle_speed_file_name) is False:
        text_font_speed = text_font_speed_medium
        text_font_speed_config_file = open(internal_media_folder + SubtitleFolder + subtitle_speed_file_name, 'w')
        text_font_speed_config_file.write(text_font_speed)
        text_font_speed_config_file.close()
        return text_font_speed
    else:
        text_font_speed_config_file = open(internal_media_folder + SubtitleFolder + subtitle_speed_file_name, 'r')
        text_font_speed = text_font_speed_config_file.readline()
        text_font_speed_config_file.close()
    return text_font_speed


def get_text_position():
    if os.path.exists(internal_media_folder + SubtitleFolder) is False:
        os.mkdir(internal_media_folder + SubtitleFolder)
    if os.path.exists(internal_media_folder + SubtitleFolder + subtitle_position_file_name) is False:
        text_font_position = text_font_position_default
        text_font_position_config_file = open(internal_media_folder + SubtitleFolder + subtitle_position_file_name, 'w')
        text_font_position_config_file.write(text_font_position)
        text_font_position_config_file.close()
        return text_font_position
    else:
        text_font_position_config_file = open(internal_media_folder + SubtitleFolder + subtitle_position_file_name, 'r')
        text_font_position = text_font_position_config_file.readline()
        text_font_position_config_file.close()
    return text_font_position

def get_text_period():
    if os.path.exists(internal_media_folder + SubtitleFolder) is False:
        os.mkdir(internal_media_folder + SubtitleFolder)
    if os.path.exists(internal_media_folder + SubtitleFolder + subtitle_period_file_name) is False:
        text_font_period = text_font_period_default
        text_font_period_config_file = open(internal_media_folder + SubtitleFolder + subtitle_period_file_name, 'w')
        text_font_period_config_file.write(str(text_font_period))
        text_font_period_config_file.close()
        return text_font_period
    else:
        text_font_period_config_file = open(internal_media_folder + SubtitleFolder + subtitle_period_file_name, 'r')
        text_font_period = text_font_period_config_file.readline()
        text_font_period_config_file.close()
    log.debug("type(text_font_period) = %s", type(text_font_period))
    log.debug("text_font_period = %s", text_font_period)
    return text_font_period


def get_text_content():
    text_content = ""
    if os.path.exists(internal_media_folder + SubtitleFolder) is False:
        os.mkdir(internal_media_folder + SubtitleFolder)
    try:
        if os.path.exists(internal_media_folder + SubtitleFolder + subtitle_file_name) is False:
            with open(internal_media_folder + SubtitleFolder + subtitle_file_name, 'w') as f:
                text_content = text_content_default
                f.write(text_content)
        else:
            with open(internal_media_folder + SubtitleFolder + subtitle_file_name, 'r') as f:
                text_contents = f.readlines()
                for i in text_contents:
                    text_content += i
    except Exception as e:
        log.debug("%s", e)
    log.debug("text_content = %s", text_content)
    return text_content

def find_ffmpeg_process():
    p = Popen("pgrep ffmpeg -a", shell=True, stdout=PIPE, stderr=PIPE)
    p_stdout, p_stderr=p.communicate()
    log.debug("p_stdout: %s", p_stdout.decode())
    log.debug("p_stderr:%s", p_stderr.decode())

def kill_all_ffmpeg_process():
    p = Popen("pkill ffmpeg", shell=True, stdout=PIPE, stderr=PIPE)


def init_reboot_params():
    time = "04:30"
    reboot_time_params = "reboot_time=" + time + "\n"
    content_lines = [
        "reboot_mode_enable=1\n",
        reboot_time_params,
    ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".reboot_config")
    config_file = open(file_uri, 'w')
    config_file.writelines(content_lines)
    config_file.close()
    os.system('sync')


def get_reboot_mode_default_from_file():
    reboot_mode = "Disable"
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".reboot_config")) is False:
        init_reboot_params()

    with open(os.path.join(led_config_dir, ".reboot_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "reboot_mode_enable" in line:
            i_reboot_mode = line.strip("\n").split("=")[1]
            if i_reboot_mode == "1":
                reboot_mode = "Enable"
                return reboot_mode
            else:
                return reboot_mode
    return reboot_mode

def get_reboot_time_default_from_file():
    reboot_time = "04:30"
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".reboot_config")) is False:
        init_reboot_params()

    with open(os.path.join(led_config_dir, ".reboot_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "reboot_time" in line:
            reboot_time = line.split("=")[1]
    log.debug("reboot_time = %s", reboot_time)
    return reboot_time


def set_reboot_params(mode, time):
    log.debug("mode : %d", mode)
    reboot_time_params = "reboot_time=" + time + "\n"
    if mode is True:
        content_lines = [
            "reboot_mode_enable=1\n",
            reboot_time_params,
        ]
    else:
        content_lines = [
            "reboot_mode_enable=0\n",
            reboot_time_params,
        ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".reboot_config")
    config_file = open(file_uri, 'w')
    config_file.writelines(content_lines)
    config_file.close()
    os.system('sync')


def set_sleep_params(start_time, end_time):
    str_sleep_start_time = "sleep_start_time=" + start_time + "\n"
    str_sleep_end_time = "sleep_end_time=" + end_time + "\n"
    content_lines = [
        str_sleep_start_time,
        str_sleep_end_time,
    ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".sleep_time_config")
    config_file = open(file_uri, 'w')
    config_file.writelines(content_lines)
    config_file.close()
    os.system('sync')


def init_sleep_time_params():
    content_lines = [
        "sleep_start_time=00:30\n",
        "sleep_end_time=04:30\n",
    ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".sleep_time_config")
    config_file = open(file_uri, 'w')
    config_file.writelines(content_lines)
    config_file.close()
    os.system('sync')


def get_sleep_time_from_file():
    s_start_time = ""
    s_end_time = ""
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".sleep_time_config")) is False:
        init_sleep_time_params()

    with open(os.path.join(led_config_dir, ".sleep_time_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "sleep_start_time" in line:
            s_start_time = line.split("=")[1].strip("\n")
        if "sleep_end_time" in line:
            s_end_time = line.split("=")[1].strip("\n")

    return s_start_time, s_end_time

def sync_playlist():
    for playlist_tmp in sorted(glob.glob(playlist_extends)):
        if os.path.isfile(playlist_tmp):
            try:
                with open(playlist_tmp, "r") as playlist_tmp_file:
                    playlist_tmp_content = playlist_tmp_file.read()
                    playlist_tmp_file.close()
            except Exception as e:
                log.debug(e)
            log.debug("playlist_tmp_content : %s", playlist_tmp_content)
            playlist_tmp_content_list = playlist_tmp_content.splitlines()
            for file_uri in playlist_tmp_content_list:
                if os.path.isfile(file_uri) is False:
                    playlist_tmp_content_list.remove(file_uri)
            log.debug("len(playlist_tmp_content_list) = %d", len(playlist_tmp_content_list))
            if len(playlist_tmp_content_list) == 0:
                log.debug("remove %s", playlist_tmp)
                os.remove(playlist_tmp)
                os.popen("sync")
            else:
                try:
                    with open(playlist_tmp, "w") as playlist_tmp_file:
                        for file_uri in playlist_tmp_content_list:
                            playlist_tmp_file.write(file_uri + "\n")

                        playlist_tmp_file.flush()
                        playlist_tmp_file.truncate()
                        playlist_tmp_file.close()
                except Exception as e:
                    log.debug(e)

def init_icled_current_gain_params_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "w") as f:
        f.writelines(["red_current_gain:3\n", "green_current_gain:3\n", "blue_current_gain:3\n"])
    f.close()

def get_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "red_current_gain" in line:
            red_current_gain = line.split(":")[1]
        elif "green_current_gain" in line:
            green_current_gain = line.split(":")[1]
        elif "blue_current_gain" in line:
            blue_current_gain = line.split(":")[1]

    # log.debug("sleep_start_time = %s", sleep_start_time)
    return red_current_gain, green_current_gain, blue_current_gain

def get_int_list_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "red_current_gain" in line:
            red_current_gain = line.split(":")[1]
        elif "green_current_gain" in line:
            green_current_gain = line.split(":")[1]
        elif "blue_current_gain" in line:
            blue_current_gain = line.split(":")[1]

    # log.debug("sleep_start_time = %s", sleep_start_time)
    return [int(red_current_gain), int(green_current_gain), int(blue_current_gain)]

def get_str_list_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "red_current_gain" in line:
            red_current_gain = line.split(":")[1]
        elif "green_current_gain" in line:
            green_current_gain = line.split(":")[1]
        elif "blue_current_gain" in line:
            blue_current_gain = line.split(":")[1]

    # log.debug("sleep_start_time = %s", sleep_start_time)
    return [red_current_gain, green_current_gain, blue_current_gain]

def get_cmd_params_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "red_current_gain" in line:
            red_current_gain = line.split(":")[1].strip("\n")
        elif "green_current_gain" in line:
            green_current_gain = line.split(":")[1].strip("\n")
        elif "blue_current_gain" in line:
            blue_current_gain = line.split(":")[1].strip("\n")

    # log.debug("sleep_start_time = %s", sleep_start_time)
    return "rgain="+red_current_gain + "," + "ggain=" + green_current_gain + "," + "bgain=" + blue_current_gain

def get_red_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "red_current_gain" in line:
            red_current_gain = line.split(":")[1].strip("\n")


    return red_current_gain

def get_green_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "green_current_gain" in line:
            green_current_gain = line.split(":")[1].strip("\n")

    return green_current_gain

def get_blue_current_gain_from_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()
        # init_reboot_params()

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "blue_current_gain" in line:
            blue_current_gain = line.split(":")[1].strip("\n")

    return blue_current_gain


def set_rgb_current_gain_to_config(str_rgain, str_ggain, str_bgain):
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_current_gain_config")) is False:
        init_icled_current_gain_params_config()

    r_gain_str = "red_current_gain:" + str_rgain + "\n"
    g_gain_str = "green_current_gain:" + str_ggain + "\n"
    b_gain_str = "blue_current_gain:" + str_bgain + "\n"

    with open(os.path.join(led_config_dir, ".icled_current_gain_config"), "w") as f:
        f.writelines([r_gain_str, g_gain_str, b_gain_str])
    f.close()



def init_led_type_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_type_config")) is False:
        with open(os.path.join(led_config_dir, ".icled_type_config"), "w") as f:
            f.writelines("icled_type:AOS")
        f.close()

def get_led_type_config():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_type_config")) is False:
        init_led_type_config()

    with open(os.path.join(led_config_dir, ".icled_type_config"), "r") as f:
        line = f.readline()
        icled_type = line.split(":")[1]
    f.close()
    log.debug("icled_type : %s", icled_type)
    return icled_type


def set_led_type_config(icled_type):
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".icled_type_config")) is False:
        init_led_type_config()
    with open(os.path.join(led_config_dir, ".icled_type_config"), "w") as f:
        f.writelines(["icled_type:" + icled_type])
    f.close()


def get_throttled_to_log():
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        try:
            get_throttled = subprocess.Popen("vcgencmd get_throttled", shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            stdout, stderr = get_throttled.communicate()
            # log.debug("get_throttled : %s", stdout.decode())
            if stdout.decode() != "throttled=0x0\n":
                log.debug("A error get_throttled : %s", stdout.decode())
            get_throttled.terminate()
        except Exception as e:
            log.debug("error!")
    else:
        pass
