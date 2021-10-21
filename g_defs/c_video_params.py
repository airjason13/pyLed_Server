from PyQt5.QtCore import QObject
import utils.log_utils
import os
from global_def import *
log = utils.log_utils.logging_init('c_led_params')

class video_params(QObject):
    def __init__(self, from_config, video_brightness, video_contrast, red_bias, green_bias, blue_bias, **kwargs):
        super(video_params, self).__init__(**kwargs)
        if from_config is True:
            self.parse_init_config()
        else:
            self.video_brightness = video_brightness
            self.video_contrast = video_contrast
            self.video_red_bias = red_bias
            self.video_green_bias = green_bias
            self.video_blue_bias = blue_bias

    def parse_init_config(self):
        # Using readlines()
        file_uri = internal_media_folder + init_config_file
        if os.path.isfile(file_uri) is False:
            L = ["brightness=30\n", "contrast=50\n", "red_bias=0\n", "green_bias=0\n", "blue_bias=0\n"]
            config_file = open(file_uri, 'w')
            config_file.writelines(L)
            config_file.close()
            os.system('sync')
        config_file = open(file_uri, 'r')
        Lines = config_file.readlines()

        count = 0
        # Strips the newline character
        for line in Lines:
            count += 1
            print("Line{}: {}".format(count, line.strip()))
            tmp = line.split("=")
            print("tmp[0] = ", tmp[0])
            print("tmp[1] = ", tmp[1])
            if tmp[0] == 'brightness':
                self.video_brightness = int(tmp[1])
            elif tmp[0] == 'contrast':
                self.video_contrast = int(tmp[1])
            elif tmp[0] == 'red_bias':
                self.video_red_bias = int(tmp[1])
            elif tmp[0] == 'green_bias':
                self.video_green_bias = int(tmp[1])
            elif tmp[0] == 'blue_bias':
                self.video_blue_bias = int(tmp[1])

    def set_video_brightness(self, br_level):
        self.video_brightness = br_level

    def set_video_contrast(self, ct_level):
        self.video_contrast = ct_level

    def set_video_red_bias(self, red_bias_level):
        self.video_red_bias = red_bias_level

    def set_video_green_bias(self, green_bias_level):
        self.green_brightness = green_bias_level

    def set_video_blue_bias(self, blue_bias_level):
        self.blue_brightness = blue_bias_level

    '''get the translated value'''
    '''0~100 mapping to -1~1'''
    def get_translated_brightness(self):
        return ((self.video_brightness - 50)/(float)(100.00))

    def get_translated_contrast(self):
        return ((self.video_contrast - 50)/(float)(100.00))
