import os
import configparser

conf_reader = configparser.ConfigParser()
conf_reader.read(os.environ['EVOPMINERCONF'])
