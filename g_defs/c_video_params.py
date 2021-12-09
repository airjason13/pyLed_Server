from PyQt5.QtCore import QObject
import utils.log_utils
import os
from global_def import *
log = utils.log_utils.logging_init('c_led_params')

class video_params(QObject):

    def __init__(self, from_config, video_brightness, video_contrast, red_bias, green_bias, blue_bias, gamma, **kwargs):
        super(video_params, self).__init__(**kwargs)
        if from_config is True:
            self.parse_init_config()
        else:
            # control by ffmpeg
            self.video_brightness = video_brightness
            self.video_contrast = video_contrast
            self.video_red_bias = red_bias
            self.video_green_bias = green_bias
            self.video_blue_bias = blue_bias

        # control by clients
        self.frame_brightness = default_led_client_brightness
        self.frame_br_divisor = default_led_client_brdivisor
        self.frame_contrast = 0
        self.frame_gamma = default_led_client_gamma

    def parse_init_config(self):
        # Using readlines()
        file_uri = internal_media_folder + init_config_file
        if os.path.isfile(file_uri) is False:
            content_lines = ["brightness=50\n", "contrast=50\n", "red_bias=0\n", "green_bias=0\n", "blue_bias=0\n"]
            config_file = open(file_uri, 'w')
            config_file.writelines(content_lines)
            config_file.close()
            os.system('sync')

        log.debug('file_uri = %s', file_uri)
        config_file = open(file_uri, 'r')
        content_lines = config_file.readlines()

        count = 0
        # Strips the newline character
        for line in content_lines:
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

    def refresh_config_file(self):
        log.debug("")
        params_birghtness = "brightness=" + str(self.video_brightness) + '\n'
        params_contrast = 'contrast=' + str(self.video_contrast) + '\n'
        params_red_bias = 'red_bias=' + str(self.video_red_bias) + '\n'
        params_green_bias = 'green_bias=' + str(self.video_green_bias) + '\n'
        params_blue_bias = 'blue_bias=' + str(self.video_blue_bias) + '\n'

        content_lines = [params_birghtness, params_contrast, params_red_bias, params_green_bias, params_blue_bias]
        file_uri = internal_media_folder + init_config_file
        config_file = open(file_uri, 'w')
        config_file.writelines(content_lines)
        config_file.close()
        os.system('sync')

    def set_video_brightness(self, br_level):
        self.video_brightness = br_level
        self.refresh_config_file()

    def set_video_contrast(self, ct_level):
        self.video_contrast = ct_level
        self.refresh_config_file()

    def set_video_red_bias(self, red_bias_level):
        self.video_red_bias = red_bias_level
        self.refresh_config_file()

    def set_video_green_bias(self, green_bias_level):
        self.video_green_bias = green_bias_level
        self.refresh_config_file()

    def set_video_blue_bias(self, blue_bias_level):
        self.video_blue_bias = blue_bias_level
        self.refresh_config_file()

    '''get the brightness translated value'''
    '''0~100 mapping to -1~1'''
    def get_translated_brightness(self):
        return (self.video_brightness - 50)*2 / float(100.00)

    '''get the contrast translated value'''
    '''0~100 mapping to -1000~1000, default = 1'''
    def get_translated_contrast(self):
        if self.video_contrast == 50:
            return 1

        return (self.video_contrast - 50) * 20

    def get_translated_redgain(self):
        return self.video_red_bias / float(100.00)

    def get_translated_greengain(self):
        return self.video_green_bias / float(100.00)

    def get_translated_bluegain(self):
        return self.video_blue_bias / float(100.00)
