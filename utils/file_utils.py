import glob
import utils.log_utils
import os
import pyudev
import psutil
import pyinotify
from global_def import *

from subprocess import check_output, CalledProcessError

log = utils.log_utils.logging_init(__file__)

def get_media_file_list(dir, with_path=False):
    log.error("dir : %s", dir)
    file_list = glob.glob(dir + "/*.mp4") + glob.glob(dir + "/*.jpg") + glob.glob(dir + "/*.jpeg") + glob.glob(dir + "/*.png")

    return file_list

def get_playlist_file_list(dir, with_path=False):
    log.debug("dir : %s", dir)
    file_list = glob.glob(dir + "/*.playlist")

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
        text_font_position_config_file = open(internal_media_folder + SubtitleFolder + subtitle_speed_file_name, 'w')
        text_font_position_config_file.write(text_font_position)
        text_font_position_config_file.close()
        return text_font_position
    else:
        text_font_position_config_file = open(internal_media_folder + SubtitleFolder + subtitle_speed_file_name, 'r')
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