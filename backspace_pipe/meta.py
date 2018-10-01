import pymel.core as pmc
import getpass
import json
import datetime
import re
from backspace_pipe import logging_control

logger = logging_control.get_logger()
time_format = "%Y.%m.%d %H:%M:%S"
pipeline_re = re.compile(r"((\w+)_)+(\d+|REF)+")


class MetaData():
    def __init__(self, fromFile=False):
        if fromFile is False:
            self.asset = self.parse_asset_name()
            self.user = getpass.getuser()
            self.time = datetime.datetime.now().strftime(time_format)
            self.comment = None
            self.recent_file = None
            self.current_file = pmc.sceneName()
        else:
            self.load_metafile()

    def parse_asset_name(self):
        match = pipeline_re.search(pmc.sceneName())
        if match is not None:
            return match.group(2)
        else:
            return ""

    def update(self):
        self.asset = self.parse_asset_name()
        self.user = getpass.getuser()
        self.time = datetime.datetime.now().strftime(time_format)

    def save_metafile(self, filepath=None):
        ''' Save metadata as json file.
        If no filepath is given, save next to current scene file.'''
        json_path = pmc.sceneName().splitext()[0] + ".json"

        json_dict = {'Asset': self.asset,
            'User': self.user,
            'Time': self.time,
            'Comment': self.comment,
            'Recent File': self.recent_file,
            'Current File': self.current_file}

        with open(json_path, 'w') as file:
            json.dump(json_dict, file, ensure_ascii=False, indent=4, sort_keys=True)

    def load_metafile(self, filepath=None):
        ''' Load metadata from json file.
        if no filepath is given, load metadata next to current scene file.'''
        json_path = pmc.sceneName().splitext()[0] + ".json"

        try:
            with open(json_path, "r") as file:
                json_dict = json.load(file)
        except IOError as e:
            logger.error("No MetaData found!")
        else:
            self.asset = json_dict["Asset"]
            self.user = json_dict["User"]
            self.time = json_dict["Time"]
            self.comment = json_dict["Comment"]
            self.recent_file = json_dict["Recent File"]
            self.current_file = json_dict["Current File"]

    def dump_to_log(self):
        logger.info("Dumping MetaData...")
        logger.info(self.asset)
        logger.info(self.user)
        logger.info(self.time)
        logger.info(self.comment)
        logger.info(self.recent_file)
        logger.info(self.current_file)
