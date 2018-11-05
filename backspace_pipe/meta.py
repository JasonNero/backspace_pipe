import pymel.core as pmc
import getpass
import json
import datetime
import re
from backspace_pipe import logging_control
import subprocess


logger = logging_control.get_logger()
time_format = "%Y.%m.%d %H:%M:%S"

'''
pipeline_re groups:
0       -> whole match
1       -> asset name
3       -> department
11      -> increment
12      -> comment
'''

pipeline_re = re.compile(r"((\w+))_((MDL)|(SHD)|(RIG)|(ANIM)|(LGT))_(((\d+)(_\w+)?)|REF)(.ma$)")


class MetaData():

    def __init__(self, fromFile=False):
        if fromFile is False:
            self.asset = self.parse_asset_name()
            self.department = self.parse_department()
            self.user = getpass.getuser()
            self.time = datetime.datetime.now().strftime(time_format)
            self.comment = None
            self.recent_file = None
            self.current_file = pmc.sceneName()
        else:
            self.load_metafile()

    def parse_asset_name(self):
        match = pipeline_re.search(pmc.sceneName().split("/")[-1])
        if match is not None:
            return match.group(1)
        else:
            return ""

    def parse_department(self):
        match = pipeline_re.search(pmc.sceneName().split("/")[-1])
        if match is not None:
            return match.group(3)
        else:
            return ""

    def update(self):
        self.asset = self.parse_asset_name()
        self.department = self.parse_department()
        self.user = getpass.getuser()
        self.time = datetime.datetime.now().strftime(time_format)
        self.current_file = pmc.sceneName()

    def save_metafile(self, filepath=None):
        ''' Save metadata as json file.
        If no filepath is given, save next to current scene file.'''
        json_path = pmc.sceneName().splitext()[0] + ".json"

        json_dict = {
            'Asset': self.asset,
            'Department': self.department,
            'User': self.user,
            'Time': self.time,
            'Comment': self.comment,
            'Recent File': self.recent_file,
            'Current File': self.current_file
        }

        # Unhide File, otherwise we get an IOError
        subprocess.check_call(["attrib", "-H", json_path], creationflags=0x08000000)

        with open(json_path, 'w') as file:
            json.dump(json_dict, file, ensure_ascii=False, indent=4, sort_keys=True)

        # Hide File, "prettier" for artist/user
        subprocess.check_call(["attrib", "+H", json_path], creationflags=0x08000000)

    # TODO: CLean this ugly mess.. maybe use dict for the whole metadata and @property for getter/setter
    def load_metafile(self, filepath=None):
        ''' Load metadata from json file.
        if no filepath is given, load metadata next to current scene file.'''
        json_path = pmc.sceneName().splitext()[0] + ".json"

        try:
            with open(json_path, "r") as file:
                json_dict = json.load(file)
        except IOError as e:
            logger.error(e)
            logger.error("No MetaData found!")
            self.__init__(fromFile=False)
        else:
            try:
                self.asset = json_dict["Asset"]
            except KeyError:
                pass

            try:
                self.department = json_dict["Department"]
            except KeyError:
                pass

            try:
                self.user = json_dict["User"]
            except KeyError:
                pass

            try:
                self.time = json_dict["Time"]
            except KeyError:
                pass

            try:
                self.comment = json_dict["Comment"]
            except KeyError:
                pass

            try:
                self.recent_file = json_dict["Recent File"]
            except KeyError:
                pass

            try:
                self.current_file = json_dict["Current File"]
            except KeyError:
                pass

    def dump_to_log(self):
        logger.info("Dumping MetaData...")
        logger.info(self.asset)
        logger.info(self.department)
        logger.info(self.user)
        logger.info(self.time)
        logger.info(self.comment)
        logger.info(self.recent_file)
        logger.info(self.current_file)
