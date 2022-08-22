import os
import glob
from main import app
from qlocalmessage import send_message
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, Response, json
from global_def import *
import traceback
from flask_wtf import Form
from wtforms import validators, RadioField, SubmitField, IntegerField
import utils.log_utils
import hashlib
import os
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
    log.debug("mp4_extends = %s", mp4_extends)
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


def find_playlist_maps():
    playlist_nest_dict = {}
    log.debug("playlist_extends = %s", playlist_extends)
    for playlist_tmp in sorted(glob.glob(playlist_extends)):
        log.debug("playlist_tmp = %s", playlist_tmp)
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
                playlist_nest_dict[playlist_name][fname] = preview_file_name

    print(playlist_nest_dict)

    return playlist_nest_dict

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


'''class TestForm(Form):
    style = {'class': 'ourClasses', 'style': 'font-size:24px;'}
    color_switcher = RadioField(
        'Led Color',
        [validators.Required()],
        choices=[('test_color:RED', 'RED'), ('test_color:GREEN', 'GREEN'), ('test_color:BLUE', 'BLUE'),
                 ('test_color:WHITE', 'WHITE')],
        default=led_color,
        render_kw=style,
        id='led_color'

    )
'''


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

    return render_template("index.html", files=maps, playlist_nest_dict=playlist_nest_dict,
                           repeat_option=routes_repeat_option, text_size=route_text_size,
                           text_content=route_text_content, text_period=20)



