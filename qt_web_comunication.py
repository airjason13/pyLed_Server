from global_def import *

tmp_clients=[]


def set_tmp_clients(c):
    global tmp_clients
    tmp_clients = c


def get_tmp_clients():
    global tmp_clients
    return tmp_clients


def get_daylight_brightness():
    return day_mode_brightness


def get_night_brightness():
    return night_mode_brightness




