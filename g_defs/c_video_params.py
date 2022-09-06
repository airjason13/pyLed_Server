from PyQt5.QtCore import QObject
import utils.log_utils
import os
import sys

from global_def import *

log = utils.log_utils.logging_init(__file__)

root_dir = os.path.dirname(sys.modules['__main__'].__file__)
led_config_dir = os.path.join(root_dir, 'video_params_config')
print("led_config_dir = ", led_config_dir)

os.makedirs(led_config_dir, exist_ok=True)

class video_params(QObject):

    def __init__(self, from_config, video_brightness, video_contrast, red_bias, green_bias, blue_bias, gamma, **kwargs):
        super(video_params, self).__init__(**kwargs)
        self.video_params_file_uri = os.path.join(led_config_dir, ".video_params_config")
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

            self.frame_brightness_algorithm = frame_brightness_adjust.auto_time_mode
            self.frame_brightness = default_led_client_brightness
            self.day_mode_frame_brightness = day_mode_brightness
            self.night_mode_frame_brightness = night_mode_brightness
            self.sleep_mode_frame_brightness = sleep_mode_brightness
            # self.frame_brightness = default_led_client_brightness
            self.frame_br_divisor = default_led_client_brdivisor
            self.frame_contrast = 0
            self.frame_gamma = gamma
            # crop function
            self.crop_start_x = 0
            self.crop_start_y = 0
            self.crop_w = 0
            self.crop_h = 0
            self.hdmi_in_crop_start_x = 0
            self.hdmi_in_crop_start_y = 0
            self.hdmi_in_crop_w = 0
            self.hdmi_in_crop_h = 0

            # still image encode peroid
            self.image_period = still_image_video_period

    def parse_init_config(self):
        # Using readlines()
        file_uri = self.video_params_file_uri  # internal_media_folder + init_config_file
        if os.path.isfile(file_uri) is False:
            content_lines = [
                            "brightness=50\n", "contrast=50\n", "red_bias=0\n", "green_bias=0\n", "blue_bias=0\n",
                            "frame_brightness_algorithm=0\n",
                            "frame_brightness=100\n", "day_mode_frame_brightness=77\n",
                            "night_mode_frame_brightness=50\n", "sleep_mode_frame_brightness=0\n",
                            "frame_br_divisor=1\n", "frame_contrast=0\n", "frame_gamma=2.2\n",
                            "image_period=60\n", "crop_start_x=0\n", "crop_start_y=0\n", "crop_w=0\n", "crop_h=0\n",
                            "hdmi_in_crop_start_x=0\n", "hdmi_in_crop_start_y=0\n",
                            "hdmi_in_crop_w=0\n", "hdmi_in_crop_h=0\n",
                             ]
            config_file = open(file_uri, 'w')
            config_file.writelines(content_lines)
            config_file.close()
            os.system('sync')
        else:
            # check all video parameters exist
            b_ret = self.check_video_params_file_valid()
            if b_ret is False:
                # re-generate video_params_file
                content_lines = [
                    "brightness=50\n", "contrast=50\n", "red_bias=0\n", "green_bias=0\n", "blue_bias=0\n",
                    "frame_brightness_algorithm=0\n",
                    "frame_brightness=100\n", "day_mode_frame_brightness=77\n",
                    "night_mode_frame_brightness=50\n", "sleep_mode_frame_brightness=0\n",
                    "frame_br_divisor=1\n", "frame_contrast=0\n", "frame_gamma=2.2\n",
                    "image_period=60\n", "crop_start_x=0\n", "crop_start_y=0\n", "crop_w=0\n", "crop_h=0\n",
                    "hdmi_in_crop_start_x=0\n", "hdmi_in_crop_start_y=0\n",
                    "hdmi_in_crop_w=0\n", "hdmi_in_crop_h=0\n",
                ]
                config_file = open(file_uri, 'w')
                config_file.writelines(content_lines)
                config_file.close()
                os.system('sync')
                pass
            else:
                pass
        log.debug('file_uri = %s', file_uri)
        config_file = open(file_uri, 'r')
        content_lines = config_file.readlines()

        count = 0
        # Strips the newline character
        for line in content_lines:
            count += 1
            log.debug("Line{}: {}".format(count, line.strip()))
            tmp = line.split("=")
            # print("tmp[0] = ", tmp[0])
            # print("tmp[1] = ", tmp[1])
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
            elif tmp[0] == 'frame_brightness_algorithm':
                self.frame_brightness_algorithm = int(tmp[1])
            elif tmp[0] == 'frame_brightness':
                self.frame_brightness = int(tmp[1])
            elif tmp[0] == 'day_mode_frame_brightness':
                self.day_mode_frame_brightness = int(tmp[1])
            elif tmp[0] == 'night_mode_frame_brightness':
                self.night_mode_frame_brightness = int(tmp[1])
            elif tmp[0] == 'sleep_mode_frame_brightness':
                self.sleep_mode_frame_brightness = int(tmp[1])
            elif tmp[0] == 'frame_br_divisor':
                self.frame_br_divisor = int(tmp[1])
            elif tmp[0] == 'frame_contrast':
                self.frame_contrast = int(tmp[1])
            elif tmp[0] == 'frame_gamma':
                self.frame_gamma = float(tmp[1])
            elif tmp[0] == 'image_period':
                self.image_period = int(tmp[1])
            elif tmp[0] == 'crop_start_x':
                self.crop_start_x = int(tmp[1])
            elif tmp[0] == 'crop_start_y':
                self.crop_start_y = int(tmp[1])
            elif tmp[0] == 'crop_w':
                self.crop_w = int(tmp[1])
            elif tmp[0] == 'crop_h':
                self.crop_h = int(tmp[1])
            elif tmp[0] == 'hdmi_in_crop_start_x':
                self.hdmi_in_crop_start_x = int(tmp[1])
            elif tmp[0] == 'hdmi_in_crop_start_y':
                self.hdmi_in_crop_start_y = int(tmp[1])
            elif tmp[0] == 'hdmi_in_crop_w':
                self.hdmi_in_crop_w = int(tmp[1])
            elif tmp[0] == 'hdmi_in_crop_h':
                self.hdmi_in_crop_h = int(tmp[1])

    def refresh_config_file(self):
        log.debug("")
        params_birghtness = "brightness=" + str(self.video_brightness) + '\n'
        params_contrast = 'contrast=' + str(self.video_contrast) + '\n'
        params_red_bias = 'red_bias=' + str(self.video_red_bias) + '\n'
        params_green_bias = 'green_bias=' + str(self.video_green_bias) + '\n'
        params_blue_bias = 'blue_bias=' + str(self.video_blue_bias) + '\n'
        params_frame_brightness = 'frame_brightness=' + str(self.frame_brightness) + '\n'
        params_frame_br_divisor = 'frame_br_divisor=' + str(self.frame_br_divisor) + '\n'
        params_frame_contrast = 'frame_contrast=' + str(self.frame_contrast) + '\n'
        params_frame_gamma = 'frame_gamma=' + str(self.frame_gamma) + '\n'
        params_image_period = 'image_period=' + str(self.image_period) + '\n'
        params_crop_start_x = 'crop_start_x=' + str(self.crop_start_x) + '\n'
        params_crop_start_y = 'crop_start_y=' + str(self.crop_start_y) + '\n'
        params_crop_w = 'crop_w=' + str(self.crop_w) + '\n'
        params_crop_h = 'crop_h=' + str(self.crop_h) + '\n'
        params_hdmi_in_crop_start_x = 'hdmi_in_crop_start_x=' + str(self.hdmi_in_crop_start_x) + '\n'
        params_hdmi_in_crop_start_y = 'hdmi_in_crop_start_y=' + str(self.hdmi_in_crop_start_y) + '\n'
        params_hdmi_in_crop_w = 'hdmi_in_crop_w=' + str(self.hdmi_in_crop_w) + '\n'
        params_hdmi_in_crop_h = 'hdmi_in_crop_h=' + str(self.hdmi_in_crop_h) + '\n'

        content_lines = [params_birghtness, params_contrast, params_red_bias, params_green_bias,
                         params_blue_bias, params_frame_brightness, params_frame_br_divisor,
                         params_frame_contrast, params_frame_gamma, params_image_period,
                         params_crop_start_x, params_crop_start_y, params_crop_w, params_crop_h,
                         params_hdmi_in_crop_start_x, params_hdmi_in_crop_start_y,
                         params_hdmi_in_crop_w, params_hdmi_in_crop_h]
        file_uri = self.video_params_file_uri   # internal_media_folder + init_config_file
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

    def set_image_peroid(self, period_value):
        self.image_period = period_value
        self.refresh_config_file()

    def set_frame_brightness(self, frame_brightness_value):
        self.frame_brightness = frame_brightness_value
        self.refresh_config_file()

    def set_frame_br_divisor(self, frame_br_divisor_value):
        self.frame_br_divisor = frame_br_divisor_value
        self.refresh_config_file()

    def set_frame_contrast(self, frame_contrast_value):
        self.frame_contrast = frame_contrast_value
        self.refresh_config_file()

    def set_frame_gamma(self, frame_gamma_value):
        self.frame_gamma = frame_gamma_value
        self.refresh_config_file()

    def set_crop_start_x(self, crop_start_x_value):
        self.crop_start_x = crop_start_x_value
        self.refresh_config_file()

    def set_crop_start_y(self, crop_start_y_value):
        self.crop_start_y = crop_start_y_value
        self.refresh_config_file()

    def set_crop_w(self, crop_w_value):
        self.crop_w = crop_w_value
        self.refresh_config_file()

    def set_crop_h(self, crop_h_value):
        self.crop_h = crop_h_value
        self.refresh_config_file()

    def set_hdmi_in_crop_start_x(self, hdmi_in_crop_start_x_value):
        self.hdmi_in_crop_start_x = hdmi_in_crop_start_x_value
        self.refresh_config_file()

    def set_hdmi_in_crop_start_y(self, hdmi_in_crop_start_y_value):
        self.hdmi_in_crop_start_y = hdmi_in_crop_start_y_value
        self.refresh_config_file()

    def set_hdmi_in_crop_w(self, hdmi_in_crop_w_value):
        self.hdmi_in_crop_w = hdmi_in_crop_w_value
        self.refresh_config_file()

    def set_hdmi_in_crop_h(self, hdmi_in_crop_h_value):
        self.hdmi_in_crop_h = hdmi_in_crop_h_value
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

    def get_frame_brightness(self):
        return self.frame_brightness

    def get_frame_br_divisor(self):
        return self.frame_br_divisor

    def get_frame_contrast(self):
        return self.frame_contrast

    def get_frame_gamma(self):
        return self.frame_gamma

    def get_crop_start_x(self):
        return self.crop_start_x

    def get_crop_start_y(self):
        return self.crop_start_y

    def get_crop_w(self):
        return self.crop_w

    def get_crop_h(self):
        return self.crop_h

    def get_hdmi_in_crop_start_x(self):
        return self.hdmi_in_crop_start_x

    def get_hdmi_in_crop_start_y(self):
        return self.hdmi_in_crop_start_y

    def get_hdmi_in_crop_w(self):
        return self.hdmi_in_crop_w

    def get_hdmi_in_crop_h(self):
        return self.hdmi_in_crop_h

    def check_video_params_file_valid(self):
        log.debug("")
        file_uri = self.video_params_file_uri
        log.debug("file_uri = %s", file_uri)
        config_file = open(file_uri, 'r')
        content_lines = config_file.readlines()
        log.debug("content_lines = %s", content_lines)
        content_tags = [
            "brightness", "contrast", "red_bias", "green_bias", "blue_bias", "frame_brightness_algorithm",
            "frame_brightness", "day_mode_frame_brightness", "night_mode_frame_brightness",
            "sleep_mode_frame_brightness",
            "frame_br_divisor", "frame_contrast", "frame_gamma",
            "image_period", "crop_start_x", "crop_start_y", "crop_w", "crop_h",
            "hdmi_in_crop_start_x", "hdmi_in_crop_start_y",
            "hdmi_in_crop_w", "hdmi_in_crop_h",
        ]

        for tag in content_tags:
            tag_found = False
            for line in content_lines:
                if tag in line:
                    tag_found = True

            if tag_found is False:
                log.debug("%s does not exist", tag)
                config_file.close()
                return False
        config_file.close()
        return True
