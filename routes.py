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


def find_maps():
    maps = {}
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

    print("maps :", maps)

    return maps


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


@app.route('/play_with_refresh_page/<filename>')
def play_with_refresh_page(filename):
    print("route play filename :", filename)
    fname = filename
    send_message(play_file=fname)
    return redirect(url_for('index'))


@app.route('/play/<filename>', methods=['POST', 'GET'])
def play(filename):
    print("route play filename :", filename)
    fname = filename
    send_message(play_file=fname)
    status_code = Response(status=200)
    return status_code
    # return redirect(url_for('index'))


@app.route('/get_thumbnail/<filename>')
def route_get_thumbnail(filename):
    log.debug("fname = %s", filename)
    return send_from_directory(internal_media_folder + ThumbnailFileFolder, filename, as_attachment=True)


@app.route("/")
def index():
    maps = find_maps()
    return render_template("index.html", files=maps)



