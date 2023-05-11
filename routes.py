import datetime
import os
import glob
from main import app
from qlocalmessage import send_message
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, Response, json
from global_def import *
import traceback
from flask_wtf import Form
from wtforms import validators, RadioField, SubmitField, IntegerField, SelectField, StringField, TimeField, DateField, \
    DateTimeField
import utils.log_utils
import hashlib
import os
import sys
from qt_web_comunication import *
from astral_hashmap import *
from g_defs.c_client import client
log = utils.log_utils.logging_init(__file__)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

routes_repeat_option = ""
route_text_size = 16
route_text_content = ""


def route_set_text_size(size):
    global route_text_size
    try:
        route_text_size = int(size)
    except Exception as e:
        log.debug(e)
        route_text_size = 16


def route_set_text_content(content):
    log.debug("content:%s", content)
    log.debug("type(content) :%s", type(content))
    global route_text_content
    route_text_content = content


def route_set_repeat_option(option):
    log.debug("option = %s", option)
    global routes_repeat_option
    if option == 0:
        routes_repeat_option = "Repeat_None"
    elif option == 1:
        routes_repeat_option = "Repeat_One"
    elif option == 2:
        routes_repeat_option = "Repeat_All"
    elif option == 3:
        routes_repeat_option = "Repeat_Random"


def find_file_maps():
    maps = {}
    # log.debug("mp4_extends = %s", mp4_extends)
    # need to add png/jpg/jpeg
    for fname in sorted(glob.glob(mp4_extends)):
        if os.path.isfile(fname):
            #key = fname
            list_file_url = fname.split("/")
            tmp_video_name = list_file_url[len(list_file_url) - 1]
            key = tmp_video_name
            prefix_video_name = tmp_video_name.split(".")[0]
            # log.debug("video_extension = %s", video_extension)
            preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
            maps[key] = preview_file_name
    for fname in sorted(glob.glob(jpg_extends)):
        if os.path.isfile(fname):
            #key = fname
            list_file_url = fname.split("/")
            tmp_video_name = list_file_url[len(list_file_url) - 1]
            key = tmp_video_name
            prefix_video_name = tmp_video_name.split(".")[0]
            # log.debug("video_extension = %s", video_extension)
            preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
            maps[key] = preview_file_name
    for fname in sorted(glob.glob(jpeg_extends)):
        if os.path.isfile(fname):
            #key = fname
            list_file_url = fname.split("/")
            tmp_video_name = list_file_url[len(list_file_url) - 1]
            key = tmp_video_name
            prefix_video_name = tmp_video_name.split(".")[0]
            # log.debug("video_extension = %s", video_extension)
            preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
            maps[key] = preview_file_name
    for fname in sorted(glob.glob(png_extends)):
        if os.path.isfile(fname):
            #key = fname
            list_file_url = fname.split("/")
            tmp_video_name = list_file_url[len(list_file_url) - 1]
            key = tmp_video_name
            prefix_video_name = tmp_video_name.split(".")[0]
            # log.debug("video_extension = %s", video_extension)
            preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
            maps[key] = preview_file_name
    print("maps :", maps)
    return maps


def get_file_list():
    file_list = []
    for fname in sorted(glob.glob(mp4_extends)):
        if os.path.isfile(fname):
            fname = fname.strip(internal_media_folder + "/")
            file_list.append(fname)
    for fname in sorted(glob.glob(jpg_extends)):
        if os.path.isfile(fname):
            fname = fname.strip(internal_media_folder + "/")
            file_list.append(fname)
    for fname in sorted(glob.glob(jpeg_extends)):
        if os.path.isfile(fname):
            fname = fname.strip(internal_media_folder + "/")
            file_list.append(fname)
    for fname in sorted(glob.glob(png_extends)):
        if os.path.isfile(fname):
            fname = fname.strip(internal_media_folder + "/")
            file_list.append(fname)

    return file_list

def get_single_file_default():
    try:
        with open(os.getcwd() + "/static/default_launch_type.dat", "r") as launch_type_config_file:
            tmp = launch_type_config_file.read()
            default_launch_type_int = tmp.split(":")[0]
            default_launch_type_params_str = tmp.split(":")[1]
            if default_launch_type_int == play_type.play_single:
                return default_launch_type_params_str
            else:
                file_list = get_file_list()
                return file_list[0]
    except Exception as e:
        log.debug(e)
    file_list = get_file_list()
    return file_list[0]

def find_playlist_maps():
    playlist_nest_dict = {}
    # log.debug("playlist_extends = %s", playlist_extends)
    for playlist_tmp in sorted(glob.glob(playlist_extends)):
        # log.debug("playlist_tmp = %s", playlist_tmp)
        if os.path.isfile(playlist_tmp):
            playlist_name_list = playlist_tmp.split("/")
            playlist_name = playlist_name_list[len(playlist_name_list) - 1]
            playlist_nest_dict[playlist_name] = {}
            f = open(playlist_tmp)
            lines = f.readlines()
            for line in lines:
                line = line.strip("\n")
                fname_url = line.split("/")
                fname = fname_url[len(fname_url) - 1]
                prefix_video_name = fname.split(".")[0]
                # log.debug("video_extension = %s", video_extension)
                preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
                # bug
                # if the fname is the same as item before, there is only one in nest!!!!!
                playlist_nest_dict[playlist_name][fname] = preview_file_name

    print(playlist_nest_dict)

    return playlist_nest_dict


def get_playlist_list():
    playlist_list = []
    for playlist_tmp in sorted(glob.glob(playlist_extends)):
        log.debug("playlist_tmp = %s", playlist_tmp)

        if os.path.isfile(playlist_tmp):
            fname_url = playlist_tmp.split("/")
            fname = fname_url[len(fname_url) - 1]
            log.debug("fname : %s", fname)
            playlist_list.append(fname)
    return playlist_list


def get_playlist_default():
    try:
        with open(os.getcwd() + "/static/default_launch_type.dat", "r") as launch_type_config_file:
            tmp = launch_type_config_file.read()
            default_launch_type_int = tmp.split(":")[0]
            default_launch_type_params_str = tmp.split(":")[1]
            if default_launch_type_int == play_type.play_playlist:
                return default_launch_type_params_str
            else:
                return get_playlist_list()[0]
    except Exception as e:
        log.debug(e)
    log.debug("get_playlist_list()[0] = %s", get_playlist_list()[0])
    return get_playlist_list()[0]

def find_maps_depreciated():
    maps = {}
    for fname in sorted(glob.glob(webp_extends)):
        if os.path.isfile(fname):
            # key = fname
            list_file_url = fname.split("/")
            key = list_file_url[len(list_file_url) - 1]
            maps[key] = round(os.path.getsize(fname) / SIZE_MB, 3)
    print("maps :", maps)

    return maps


def get_nest_maps(maps):
    dict_list = []
    for x in maps:
        fl_dic = {}
        try:
            print("x: ", x)
            fl_dic["filename"] = x
            fl_dic["size"] = maps[x]
        except:
            print(traceback.print_exc())
        dict_list.append(fl_dic)
    print("nest_dict :", dict_list)
    return dict_list


def get_reboot_time_default():
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

def get_sleep_start_time_default():
    sleep_start_time = "11:50"
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".sleep_time_config")) is False:
        init_sleep_time_params()
        # init_reboot_params()

    with open(os.path.join(led_config_dir, ".sleep_time_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "sleep_start_time" in line:
            sleep_start_time = line.split("=")[1]
    log.debug("sleep_start_time = %s", sleep_start_time)
    return sleep_start_time


def get_sleep_end_time_default():
    sleep_end_time = "11:50"
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".sleep_time_config")) is False:
        init_sleep_time_params()
        # init_reboot_params()

    with open(os.path.join(led_config_dir, ".sleep_time_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        if "sleep_end_time" in line:
            sleep_end_time = line.split("=")[1]
    log.debug("sleep_end_time = %s", sleep_end_time)
    return sleep_end_time


@app.route('/play_with_refresh_page/<filename>')
def play_with_refresh_page(filename):
    log.debug("route play filename : %s", filename)
    fname = filename
    send_message(play_file=fname)
    return redirect(url_for('index'))


@app.route('/play/<filename>', methods=['POST'])
def play(filename):
    log.debug("route play filename :%s", filename)
    fname = filename
    send_message(play_file=fname)
    status_code = Response(status=200)
    return status_code


@app.route('/play_playlist/<playlist>', methods=['POST'])
def play_playlist(playlist):
    log.debug("route play playlist : %s", playlist)
    fname = playlist
    send_message(play_playlist=fname)
    status_code = Response(status=200)
    return status_code


@app.route('/play_hdmi_in/<cmd>', methods=['POST'])
def play_hdmi_in(cmd):
    log.debug("route hdmi_in cmd : %s ", cmd)
    send_message(play_hdmi_in=cmd)
    status_code = Response(status=200)
    return status_code

@app.route('/play_cms/<cmd>', methods=['POST'])
def play_cms(cmd):
    log.debug("route cms_start cmd : %s ", cmd)
    send_message(play_cms=cmd)
    status_code = Response(status=200)
    return status_code

@app.route('/configure_wifi/<data>', methods=['POST'])
def configure_wifi(data):
    log.debug("configure_wifi data : %s ", data)
    band = ""
    channel = ""

    if os.path.exists("/usr/bin/configure_hotspot_alfa.sh") is False:
        log.debug("alfa hotspot configure script is not exist")
    else:
        if "2.4G" in data:
            band = "bg"
        elif "5G" in data:
            band = "a"
        else:
            return Response(status=200)

        tmp = str(data).split("=")
        channel = tmp[len(tmp) - 1]
        cmd = "configure_hotspot_alfa.sh " + band + " " + channel

        os.system(cmd)

        cmd = "sync"
        os.system(cmd)

        cmd = "reboot"
        os.system(cmd)

    status_code = Response(status=200)
    return status_code


@app.route('/set_text_size/<size>', methods=['POST'])
def set_text_size(size):
    log.debug("route set_text_size size : %s", str(size))
    send_message(set_text_size=str(size))
    status_code = Response(status=200)
    return status_code


@app.route('/set_text_speed/<speed>', methods=['POST'])
def set_text_speed(speed):
    log.debug("route set_text_speed speed : %s", str(speed))
    send_message(set_text_speed=str(speed))
    status_code = Response(status=200)
    return status_code


@app.route('/set_text_position/<position>', methods=['POST'])
def set_text_position(position):
    log.debug("route set_text_position position : %s", str(position))
    send_message(set_text_position=str(position))
    status_code = Response(status=200)
    return status_code


@app.route('/set_text_period/<period>', methods=['POST'])
def set_text_period(period):
    log.debug("route set_text_period period : %s", str(period))
    send_message(set_text_period=str(period))
    status_code = Response(status=200)
    return status_code


@app.route('/start_color_test/<data>', methods=['POST'])
def start_color_test(data):
    send_message(start_color_test=data)
    status_code = Response(status=200)
    return status_code


@app.route('/play_text/<data>', methods=['POST'])
def play_text(data):
    log.debug("route play_text data %s:", data)

    send_message(play_text=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_repeat_option/<data>', methods=['POST'])
def set_repeat_option(data):
    log.debug("route play_text data : %s", data)

    send_message(set_repeat_option=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_frame_brightness_option/<data>', methods=['POST'])
def set_frame_brightness_option(data):
    log.debug("route set_frame_brightness_option data : %s", data)

    send_message(set_frame_brightness_option=data)
    status_code = Response(status=200)
    return status_code


@app.route('/create_new_playlist/<data>', methods=['POST'])
def create_new_playlist(data):
    if os.path.exists(internal_media_folder + PlaylistFolder) is False:
        os.mkdir(internal_media_folder + PlaylistFolder)

    log.debug("route create_new_playlist data : %s", data)
    try:
        playlist_uri = internal_media_folder + PlaylistFolder + data.split(";")[0].split(":")[1] + ".playlist"
        file_name = data.split(";")[1].split(":")[1]
        log.debug("playlist_uri = %s", playlist_uri)
        if playlist_uri is not None and file_name is not None:
            playlist_file = open(playlist_uri, "w+")
            log.debug("file_name = %s", file_name)
            file_uri = internal_media_folder + "/" + file_name + "\n"
            log.debug("file_uri = %s", file_uri)
            playlist_file.write(file_uri)
            playlist_file.flush()
            playlist_file.truncate()
            playlist_file.close()
    except Exception as e:
        log.debug(e)

    # send_message(set_frame_brightness_option=data)
    # status_code = Response(status=200)
    # return status_code
    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json

    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)
    # print("playlist_json : " + playlist_json)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.truncate()
    playlist_js_file.close()

    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           brightnessvalues=brightnessvalues)

def get_default_play_mode_default():
    try:
        str_ret = ""
        with open(os.getcwd() + "/static/default_launch_type.dat", "r") as launch_type_config_file:
            tmp = launch_type_config_file.readline()
            log.debug("launch_type_config : %s", tmp)
            default_launch_type_int = int(tmp.split(":")[0])
            default_launch_params_str = tmp.split(":")[1]
            if default_launch_type_int == 0:
                str_ret = "none_mode"
            elif default_launch_type_int == 1:
                str_ret = "single_file_mode"
            elif default_launch_type_int == 2:
                str_ret = "playlist_mode"
            elif default_launch_type_int == 3:
                if "AIO" in get_led_role():
                    str_ret = "none_mode"
                else:
                    str_ret = "hdmi_in_mode"
            elif default_launch_type_int == 4:
                if "AIO" in get_led_role():
                    str_ret = "none_mode"
                else:
                    str_ret = "cmd_mode"
            log.debug("str_ret :%s", str_ret)
            return str_ret
    except Exception as e:
        log.debug(e)
    return "none_mode"


def get_brightness_mode_default():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')

    str_ret = 'fix_mode'
    log.debug("video_params file is %s: ", os.path.join(led_config_dir, ".video_params_config"))
    if os.path.exists(os.path.join(led_config_dir, ".video_params_config")) is False:
        init_video_params()

    with open(os.path.join(led_config_dir, ".video_params_config"), "r+") as f:
        lines = f.readlines()
    for line in lines:
        if "frame_brightness_algorithm" in line:
            tmp = line.strip("\n").split("=")[1]
            if int(tmp) == 0:
                str_ret = 'fix_mode'
            elif int(tmp) == 1:
                str_ret = 'auto_time_mode'
            elif int(tmp) == 2:
                str_ret = 'auto_als_mode'
            elif int(tmp) == 3:
                str_ret = 'test_mode'
    f.close()
    return str_ret


def init_video_params():
    content_lines = [
        "brightness=50\n", "contrast=50\n", "red_bias=0\n", "green_bias=0\n", "blue_bias=0\n",
        "sleep_mode_enable=1\n", "target_city_index=0\n",
        "frame_brightness_algorithm=0\n",
        "frame_brightness=50\n", "day_mode_frame_brightness=50\n",
        "night_mode_frame_brightness=30\n", "sleep_mode_frame_brightness=0\n",
        "frame_br_divisor=1\n", "frame_contrast=0\n", "frame_gamma=2.2\n",
        "image_period=60\n", "crop_start_x=0\n", "crop_start_y=0\n", "crop_w=0\n", "crop_h=0\n",
        "hdmi_in_crop_start_x=0\n", "hdmi_in_crop_start_y=0\n",
        "hdmi_in_crop_w=0\n", "hdmi_in_crop_h=0\n",
    ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".video_params_config")
    config_file = open(file_uri, 'w')
    config_file.writelines(content_lines)
    config_file.close()
    os.system('sync')


def init_reboot_params():
    content_lines = [
        "reboot_mode_enable=1\n",
        "reboot_time=04:30\n",
    ]
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    file_uri = os.path.join(led_config_dir, ".reboot_config")
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


def get_brightness_value_default():
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    brightness_values_maps = {}
    led_role = get_led_role()
    str_fr_br = "0"
    str_fr_br_day_mode = "0"
    str_fr_br_night_mode = "0"
    str_fr_br_sleep_mode = "0"
    log.debug("video_params file is %s: ", os.path.join(led_config_dir, ".video_params_config"))
    if os.path.exists(os.path.join(led_config_dir, ".video_params_config")) is False:
        init_video_params()

    with open(os.path.join(led_config_dir, ".video_params_config"), "r") as f:
        lines = f.readlines()

    for line in lines:
        tag = line.split("=")[0]
        if "frame_brightness" == tag:
            str_fr_br = line.strip("\n").split("=")[1]
            brightness_values_maps["frame_brightness"] = str_fr_br
        elif "day_mode_frame_brightness" == tag:
            str_fr_br_day_mode = line.strip("\n").split("=")[1]
            if "Server" in led_role:
                brightness_values_maps["day_mode_frame_brightness"] = str_fr_br_day_mode
        elif "night_mode_frame_brightness" == tag:
            str_fr_br_night_mode = line.strip("\n").split("=")[1]
            if "Server" in led_role:
                brightness_values_maps["night_mode_frame_brightness"] = str_fr_br_night_mode
        elif "sleep_mode_frame_brightness" == tag:
            str_fr_br_sleep_mode = line.strip("\n").split("=")[1]
            if "Server" in led_role:
                brightness_values_maps["sleep_mode_frame_brightness"] = str_fr_br_sleep_mode

    f.close()
    log.debug("str_fr_br : %s", str_fr_br)
    log.debug("str_fr_br_day_mode : %s", str_fr_br_day_mode)
    log.debug("str_fr_br_night_mode : %s", str_fr_br_night_mode)
    log.debug("str_fr_br_sleep_mode : %s", str_fr_br_sleep_mode)
    return brightness_values_maps


def get_sleep_mode_default():
    sleep_mode = "Disable"
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".video_params_config")) is False:
        init_video_params()

    with open(os.path.join(led_config_dir, ".video_params_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        tag = line.split("=")[0]
        if "sleep_mode_enable" == tag:
            i_sleep_mode = line.strip("\n").split("=")[1]
            if i_sleep_mode == "1":
                sleep_mode = "Enable"
                return sleep_mode
            else:
                return sleep_mode
    return sleep_mode


def get_reboot_mode_default():
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
                log.debug("reboot_mode : %s", reboot_mode)
                return reboot_mode
            else:
                log.debug("reboot_mode : %s", reboot_mode)
                return reboot_mode
    log.debug("reboot_mode : %s", reboot_mode)
    return reboot_mode


def get_target_city_default():
    city_index = 0
    target_city = City_Map[city_index].get("City")
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)
    led_config_dir = os.path.join(root_dir, 'video_params_config')
    if os.path.isfile(os.path.join(led_config_dir, ".video_params_config")) is False:
        init_video_params()

    with open(os.path.join(led_config_dir, ".video_params_config"), "r") as f:
        lines = f.readlines()
    f.close()
    for line in lines:
        tag = line.split("=")[0]
        if tag == "target_city_index":
            city_index = int(line.strip("\n").split("=")[1])
            target_city = City_Map[city_index].get("City")
    return target_city


def get_city_hash_map():
    city_hash_map = {}
    for city in City_Map:
        city_hash_map[city.get("City")] = city.get("City")
    print(city_hash_map)
    return city_hash_map


def get_city_list():
    city_list = []
    for city in City_Map:
        city_list.append(city.get("City"))

    return city_list

class LaunchTypeForm(Form):
    # default play mode switcher
    style = {'class': 'ourClasses', 'style': 'font-size:24px;color:white', }
    if "AIO" in get_led_role():
        launch_type_switcher = RadioField(
            label="Default Play Mode",
            id="default_play_mode_switcher",
            choices=[('none_mode', 'None MODE'),
                     ('single_file_mode', 'Single File Mode'),
                     ('playlist_mode', 'Playlist Mode')],
            default=get_default_play_mode_default(),
            render_kw=style,
        )
    else:
        launch_type_switcher = RadioField(
            label="Default Play Mode",
            id="default_play_mode_switcher",
            choices=[('none_mode', 'None MODE'),
                     ('single_file_mode', 'Single File Mode'),
                     ('playlist_mode', 'Playlist Mode'),
                     ('hdmi_in_mode', 'HDMI-In Mode'),
                     ('cms_mode', 'CMS Mode')],
            default=get_default_play_mode_default(),
            render_kw=style,
        )

    # single file list
    single_file_selectfield_style = {'class': 'ourClasses',
                                     'style': 'font-size:24px;color:black;size:320px;width:300px', }
    single_file_selectfiled = SelectField(
        "Default Play File Name",
        id="single_file_selected",
        # choices=get_city_hash_map(),
        choices=get_file_list(),
        default=get_single_file_default(),
        render_kw=single_file_selectfield_style,
    )

    # playlist list
    playlist_selectfield_style = {'class': 'ourClasses',
                                     'style': 'font-size:24px;color:black;size:320px;width:300px', }
    playlist_selectfield = SelectField(
        "Default Playlist Name",
        id="playlist_selected",
        # choices=get_city_hash_map(),
        choices=get_playlist_list(),
        default=get_playlist_default(),
        render_kw=single_file_selectfield_style,
    )


class BrightnessAlgoForm(Form):

    style = {'class': 'ourClasses', 'style': 'font-size:24px;color:white', }
    brightness_mode_switcher = RadioField(

            label="Brightness Mode",
            id="brightness_mode_switcher",
            choices=[('fix_mode', 'FIX MODE'),
                     ('auto_time_mode', 'Time Mode'),
                     ('auto_als_mode', 'ALS Mode'),
                     ('test_mode', 'Test Mode')],
            default=get_brightness_mode_default(),

            render_kw=style,

        )
    # style = {'class': 'ourClasses', 'style': 'font-size:24px;color:white', }
    sleep_mode_switcher = RadioField(
        "Sleep Mode",
        id="sleep_mode_switcher",
        choices=[('Disable', 'Disable'),
                 ('Enable', 'Enable'),
                 ],
        default=get_sleep_mode_default(),
        render_kw=style,

    )
    city_style = {'class': 'ourClasses', 'style': 'font-size:24px;color:black;size:320px;width:200px', }
    city_selectfiled = SelectField(
        "City",
        id="city_selected",
        # choices=get_city_hash_map(),
        choices=get_city_list(),
        default=get_target_city_default(),
        render_kw=city_style,
    )

    reboot_style = {'class': 'ourClasses', 'style': 'font-size:24px;color:black;size:320px;width:200px', }
    reboot_mode_switcher = RadioField(
        "Reboot Mode",
        id="reboot_mode_switcher",
        choices=[('Disable', 'Disable'),
                 ('Enable', 'Enable'),
                 ],
        default=get_reboot_mode_default(),
        render_kw=style,
    )


@app.route('/remove_media_file/<data>', methods=['POST'])
def remove_media_file(data):
    log.debug("route remove_media_file data : %s", data)
    file_uri = internal_media_folder + "/" + data
    log.debug("file_uri : %s", file_uri)
    if os.path.isfile(file_uri) is True:
        log.debug("file_uri exists")
        os.remove(file_uri)
        list_file_url = file_uri.split("/")
        tmp_video_name = list_file_url[len(list_file_url) - 1]
        key = tmp_video_name
        prefix_video_name = tmp_video_name.split(".")[0]
        # log.debug("video_extension = %s", video_extension)
        preview_file_name = hashlib.md5(prefix_video_name.encode('utf-8')).hexdigest() + ".webp"
        preview_file_uri = internal_media_folder + "/" + ThumbnailFileFolder + preview_file_name
        if os.path.isfile(preview_file_uri) is True:
            log.debug("preview_file_uri exists")
            os.remove(preview_file_uri)
            os.popen("sync")
            # remove file in playlist
            for playlist_tmp in sorted(glob.glob(playlist_extends)):
                log.debug("playlist_tmp = %s", playlist_tmp)
                if os.path.isfile(playlist_tmp):
                    playlist_fd = open(playlist_tmp, "r")
                    lines = playlist_fd.readlines()
                    playlist_fd.close()
                    playlist_fd = open(playlist_tmp, "w")
                    for line in lines:
                        if line.strip("\n") != file_uri:
                            playlist_fd.write(line)
                    playlist_fd.flush()
                    playlist_fd.truncate()
                    playlist_fd.close()

    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    # handle remove file uri in playlists
    for playlist in playlist_nest_dict:
        log.debug("playlist :%s ", playlist)
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json

    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.truncate()
    playlist_js_file.close()

    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           brightnessvalues=brightnessvalues)


@app.route('/set_sleep_mode/<data>', methods=['POST'])
def set_sleep_mode(data):
    log.debug("set_sleep_mode, data = %s", data)

    send_message(set_sleep_mode=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_reboot_mode/<data>', methods=['POST'])
def set_reboot_mode(data):
    log.debug("set_reboot_mode, data = %s", data)

    send_message(set_reboot_mode=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_reboot_time/<data>', methods=['POST'])
def set_reboot_time(data):
    log.debug("set_reboot_time, data = %s", data)

    send_message(set_reboot_time=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_sleep_time/<data>', methods=['POST'])
def set_sleep_time(data):
    log.debug("set_sleep_time, data = %s", data)

    send_message(set_sleep_time=data)
    status_code = Response(status=200)
    return status_code


@app.route('/set_target_city/<data>', methods=['POST'])
def set_target_city(data):
    log.debug("set_target_city, data = %s", data)

    send_message(set_target_city=data)
    status_code = Response(status=200)
    return status_code

@app.route('/set_brightness_algo/<data>', methods=['POST'])
def set_brightness_algo(data):
    log.debug("set_brightness_algo data :" + data)
    send_message(set_brightness_algo=data)
    status_code = Response(status=200)
    return status_code

@app.route('/set_brightness_values/<data>', methods=['POST'])
def set_brightness_values(data):
    log.debug("set_brightness_values data :" + data)
    send_message(set_frame_brightness_values_option=data)
    status_code = Response(status=200)
    return status_code

@app.route('/set_default_play_mode/<data>', methods=['POST'])
def set_default_play_mode(data):
    log.debug("set_default_play_mode data :" + data)
    send_message(set_default_play_mode_option=data)
    status_code = Response(status=200)
    return status_code

@app.route('/add_to_playlist/<data>', methods=['POST'])
def add_to_playlist(data):
    log.debug("add_to_playlist data:%s", data)
    playlist_name = data.split(";")[0].split(":")[1]
    playlist_uri = internal_media_folder + PlaylistFolder + playlist_name
    file_name = data.split(";")[1].split(":")[1]
    file_uri = internal_media_folder + "/" + file_name
    log.debug("file_name:%s, playlist_name:%s", file_name, playlist_name)
    log.debug("file_uri:%s, playlist_uri:%s", file_uri, playlist_uri)
    playlist_fd = open(playlist_uri, "a")
    playlist_fd.write(file_uri + "\n")
    playlist_fd.flush()
    playlist_fd.truncate()
    playlist_fd.close()
    os.popen("sync")

    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    # handle remove file uri in playlists
    for playlist in playlist_nest_dict:
        log.debug("playlist :%s ", playlist)
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json

    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.truncate()
    playlist_js_file.close()

    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           brightnessvalues=brightnessvalues)


@app.route('/remove_playlist/<data>', methods=['POST'])
def remove_playlist(data):
    log.debug("remove_playlist : %s", data)

    playlist_uri = internal_media_folder + PlaylistFolder + data
    if os.path.isfile(playlist_uri):
        os.remove(playlist_uri)
        os.popen("sync")

    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    # handle remove file uri in playlists
    for playlist in playlist_nest_dict:
        log.debug("playlist :%s ", playlist)
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json

    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.truncate()
    playlist_js_file.close()

    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           brightnessvalues=brightnessvalues)

@app.route('/remove_file_from_playlist/<data>', methods=['POST'])
def remove_file_from_playlist(data):
    log.debug("remove_file_from_playlist : %s", data)
    playlist_uri = internal_media_folder + PlaylistFolder + data.split(";")[0].split(":")[1]
    file_uri = internal_media_folder + PlaylistFolder + data.split(";")[1].split(":")[1]
    log.debug("playlist_uri : %s", playlist_uri)
    log.debug("file_uri : %s", file_uri)
    if os.path.isfile(playlist_uri):
        with open(playlist_uri, "r") as fr:
            lines = fr.readlines()
            fr.close()
        with open(playlist_uri, "w") as fw:
            for line in lines:
                if line.strip("\n") != file_uri:
                    fw.write(line)
                    fw.flush()
                    fw.truncate()
                    fw.close()

    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    # handle remove file uri in playlists
    for playlist in playlist_nest_dict:
        log.debug("playlist :%s ", playlist)
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json

    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.truncate()
    playlist_js_file.close()
    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           brightnessvalues=brightnessvalues)


@app.route('/set_ledserver_reboot_option/', methods=['POST'])
def set_ledserver_reboot_option():
    log.debug("route set_ledserver_reboot_option")

    k = os.popen("reboot")
    k.close()

    status_code = Response(status=200)
    return status_code


@app.route('/set_ledclients_reboot_option/', methods=['POST'])
def set_ledclients_reboot_option():
    log.debug("route set_ledclients_reboot_option")
    data = "true"
    send_message(set_ledclients_reboot_option=data)

    status_code = Response(status=200)
    return status_code


@app.route('/get_thumbnail/<filename>')
def route_get_thumbnail(filename):
    # log.debug("fname = %s", filename)
    return send_from_directory(internal_media_folder + ThumbnailFileFolder, filename, as_attachment=True)


@app.route("/test_page")
def test_page():
    return render_template("test_page.html")


@app.route("/")
def index():
    maps = find_file_maps()
    playlist_nest_dict = find_playlist_maps()
    log.debug("playlist_maps = %s", playlist_nest_dict)
    log.debug("routes_repeat_option = %s", routes_repeat_option)
    import json
    playlist_js_file = open("static/playlist.js", "w")
    playlist_json = json.dumps(playlist_nest_dict)

    playlist_js_file.write("var jsonstr = " + playlist_json)
    playlist_js_file.flush()
    playlist_js_file.truncate()
    playlist_js_file.close()

    # get client information
    # tmp_clients = get_tmp_clients()
    # log.debug("len(tmp_clients)  =%d", len(tmp_clients))
    # log.debug("tmp_clients[0].client_ip  =%s", tmp_clients[0].client_ip)
    # test_city = get_city_hash_map()
    # print(test_city)
    # print(type(test_city))
    # test_city_list = get_city_list()
    # print(test_city_list)
    # print(type(test_city_list))
    # brightness Algo radio form
    brightnessAlgoform = BrightnessAlgoForm()
    brightnessAlgoform.sleep_mode_switcher.data=get_sleep_mode_default()
    brightnessAlgoform.city_selectfiled.data=get_target_city_default()
    brightnessAlgoform.reboot_mode_switcher.data=get_reboot_mode_default()
    # print(type(brightnessAlgoform.city_selectfiled.choices))
    brightnessAlgoform.brightness_mode_switcher.data=get_brightness_mode_default()

    default_play_form = LaunchTypeForm()
    default_play_form.launch_type_switcher.data = get_default_play_mode_default()
    default_play_form.single_file_selectfiled.data = get_single_file_default()
    default_play_form.playlist_selectfield.data = get_playlist_default()
    # get brightness setting values
    brightnessvalues = get_brightness_value_default()
    reboot_time = get_reboot_time_default()
    sleep_start_time = get_sleep_start_time_default()
    sleep_end_time = get_sleep_end_time_default()
    role=get_led_role()
    log.debug("role = %s", role)

    return render_template("index.html", title="GIS TLED", ledrole=role, sw_version=version, files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20, form=brightnessAlgoform,
                           default_play_form=default_play_form,
                           brightnessvalues=brightnessvalues, reboot_time=reboot_time,
                           sleep_start_time=sleep_start_time, sleep_end_time=sleep_end_time)



