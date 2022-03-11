import os
import sys
from global_def import *
import utils.log_utils
log = utils.log_utils.logging_init(__file__)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
root_dir = os.path.dirname(sys.modules['__main__'].__file__)
led_config_dir = os.path.join(root_dir, 'led_config')
print("led_config_dir = ", led_config_dir)

os.makedirs(led_config_dir, exist_ok=True)

class Led_Config(QObject):
	def __init__(self, **kwargs):
		super(Led_Config, self).__init__(**kwargs)
		self.led_config_file_uri = os.path.join(led_config_dir, ".led_config")
		log.debug("self.led_config_file_uri = %s", self.led_config_file_uri)
		if os.path.exists(self.led_config_file_uri) is True:
			log.debug("led config file exist")
		else:
			log.debug("led config file not exist")
			self.led_config_file = open(self.led_config_file_uri, "a")
			self.led_config_file.write("led_width:" + str(default_led_wall_width) + "\n")
			self.led_config_file.write("led_height:" + str(default_led_wall_height) + "\n")
			self.led_config_file.close()

	def get_led_wall_width(self):
		width = 0
		with open(self.led_config_file_uri) as f:
			line = "temp"
			while line:
				line = f.readline()
				if "led_width" in line:
					width = int(line.split(":")[1])
					log.debug("width = %s", width)
					break
		return width

	def get_led_wall_height(self):
		height = 0
		with open(self.led_config_file_uri) as f:
			line = "temp"
			while line:
				line = f.readline()
				if "led_height" in line:
					height = int(line.split(":")[1])
					log.debug("height = %s", height)
					break
		return height

	def set_led_wall_res(self, width, height):
		file = open(self.led_config_file_uri, "r")
		replacement = ""
		# using the for loop
		for line in file:
			line = line.strip()
			log.debug("%s", line)
			if "led_width" in line:
				changes = line.replace(line, "led_width:" + str(width))
			elif "led_height" in line:
				changes = line.replace(line, "led_height:" + str(height))
			else:
				changes = line
			replacement = replacement + changes + "\n"

		file.close()
		# opening the file in write mode
		fout = open(self.led_config_file_uri, "w")
		fout.write(replacement)
		fout.close()

