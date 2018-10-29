import pymel.core as pmc
import re
import os
import shutil

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets

from backspace_pipe.meta import MetaData
from backspace_pipe import logging_control

logger = logging_control.get_logger()

instance = None


def get_maya_window():
    # Get Maya Window Pointer (py2: long(pointer), py3: pointer)
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtWidgets.QWidget)


def get_instance():
    global instance
    if not instance:
        instance = SceneControl()
        return instance
    else:
        return instance


class SceneControl():
    meta = None
    incr_padding = 3

    def __init__(self):
        self.meta = MetaData()
        global instance
        if not instance:
            instance = self

    def load_incr(self, incr):
        ''' Load increment of current Asset by number.'''
        curr_path = pmc.sceneName()

        re_incr = re.compile(r"_({incr:0{width}d})(_\w+)?(.ma$)".format(incr=incr, width=self.incr_padding))

        for root, subdirs, files in os.walk(curr_path.parent):
            for file in files:
                match = re_incr.search(file)

                if match is None:
                    continue

                incr_file = os.path.join(root, file)

        if incr_file is None:
            logger.error("Could not find increment {incr:0{width}d} of asset {asset}!".format(incr=incr, width=self.incr_padding, asset=self.meta.asset))
            return False
        else:
            self.load(incr_file)
            return True

    # FIX OPENING WRONG DEPARTMENT INCREMENTALS
    def load_latest_incr(self):
        ''' Load latest increment of current Asset. '''
        re_incr = re.compile(r"{asset_name}_(\d+)(_\w+)?(.ma$)".format(asset_name = self.meta.asset))

        asset_path = pmc.Path(self.meta.current_file).parent

        logger.info("Asset Path: {}".format(asset_path))

        latest_incr_int = 0
        latest_incr_file = None

        for root, subdirs, files in os.walk(asset_path):
            for file in files:
                match = re_incr.search(file)

                if match is None:
                    continue

                curr_incr_int = int(match.group(1).replace("_", ""))

                if curr_incr_int > latest_incr_int:
                    latest_incr_int = curr_incr_int
                    latest_incr_file = os.path.join(root, file)

        if latest_incr_file is None:
            logger.error("Could not find latest increment of asset {asset}!".format(asset=self.meta.asset))
            return False
        else:
            self.load(latest_incr_file)
            return True

    def load_dialogue(self):
        selected_file = pmc.fileDialog2(
            fileMode=1, fileFilter="*.ma *.mb", dialogStyle=2,
            dir=pmc.workspace.path / pmc.workspace.fileRules["mayaAscii"])
        if selected_file:
            self.load(file=selected_file[0])

    def load(self, file):
        ''' Wraps pymels load scene according to pipeline definitions. '''
        logger.info("Opening file {} ...".format(file))
        try:
            pmc.openFile(file)
        except RuntimeError as e:
            logger.warning(e)
            confirmation = pmc.confirmDialog(
                title='Confirm', message="{}Force Open?".format(e), button=['Yes', 'No'],
                defaultButton='Yes', cancelButton='No', dismissString='No')
            if confirmation == 'Yes':
                pmc.openFile(file, force=True)
            else:
                return False

        self.meta = MetaData(fromFile=True)
        # self.meta.dump_to_log()
        return True

    def save_dialogue(self):
        selected_file = pmc.fileDialog2(
            fileMode=0, fileFilter="*.ma *.mb", dialogStyle=2,
            dir=pmc.workspace.path / pmc.workspace.fileRules["mayaAscii"])
        if selected_file:
            self.save_as(file=selected_file[0])

    def save(self, comment=None):
        ''' Wraps pymel save scene according to pipeline definitions. '''

        self.meta.update()
        # self.meta.comment = comment
        self.meta.save_metafile()

        logger.info("Saving file...")
        # self.meta.dump_to_log()
        try:
            pmc.saveFile()
        except RuntimeError as e:
            logger.error(e)
            return False

        if "Student" in get_maya_window().windowTitle():
            self.del_maya_lic_string()
        return True

    def save_as(self, file, comment=None):
        ''' Wraps pymel saveAs scene according to pipeline definitions. '''

        if not comment:
            result = pmc.promptDialog(
                title="Comment", message="Enter Comment:", button=["OK", "Cancel"],
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel")
            if result == "OK":
                comment = pmc.promptDialog(query=True, text=True)
            else:
                return False

        recent_file = pmc.sceneName()
        logger.info("Saving as {} ...".format(file))
        # self.meta.dump_to_log()
        try:
            pmc.saveAs(file)
        except RuntimeError as e:
            logger.error(e)
            return False

        if "Student" in get_maya_window().windowTitle():
            self.del_maya_lic_string()

        # Create and save MetaData for new file
        self.meta = MetaData()
        self.meta.recent_file = recent_file
        self.meta.comment = comment
        self.meta.save_metafile()
        return True

    def save_incr(self, comment=None):
        ''' Increment Scene. '''
        curr_path = pmc.sceneName()
        curr_name, curr_ext = curr_path.name.splitext()

        re_incr = re.compile(r"_\d+")
        matches = re_incr.findall(curr_name)

        if len(matches) == 0:
            logger.warning("Please check filename format: 'your_asset_name_XX_optional_comment.ma'!")
            return False
        else:
            match = matches[-1]

        curr_asset = curr_name.split(match)[0]

        curr_incr_str = match.replace("_", "")

        new_incr_int = int(curr_incr_str) + 1

        # "_{num:0{width}d}" creates the increment suffix with leading zeroes
        new_incr_str = "_{num:0{width}d}".format(num=new_incr_int, width=self.incr_padding)

        incr_file = pmc.Path(curr_path.parent + "/" + curr_asset + new_incr_str + curr_ext)

        if os.path.exists(incr_file):
            logger.error("FILE ALREADY EXITS!")
            confirmation = pmc.confirmDialog(
                title='Confirm', message="{}Force Save?".format(e), button=['Yes', 'No'],
                defaultButton='Yes', cancelButton='No', dismissString='No')
            if confirmation == 'Yes':
                self.save_as(incr_file, comment)
            else:
                return False

        else:
            return self.save_as(incr_file, comment)

    def publish(self, comment=None):
        ''' Publish scene with comment. '''

        if not comment:
            result = pmc.promptDialog(
                title="Comment", message="Enter Comment:", button=["OK", "Cancel"],
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel")
            if result == "OK":
                comment = pmc.promptDialog(query=True, text=True)
            else:
                return False

        curr_path = pmc.sceneName()
        curr_name, curr_ext = curr_path.name.splitext()

        re_incr = re.compile(r"_\d+")
        curr_asset = re_incr.split(curr_name)[0]

        new_path = pmc.Path(curr_path.parent.parent + "/" + curr_asset + "_REF" + curr_ext)

        self.save_as(new_path, comment)
        return True

    def del_maya_lic_string(self):
        ''' Deletes the license info in the mayaAscii file. '''
        logger.debug("Maya License String")

        # Get Scene Path
        filePath = pmc.sceneName()

        if filePath.splitext()[-1] == ".mb":
            logger.warning("Scene needs to be saved as .ma!")
            return False

        bakPath = filePath + ".bak"

        # Closing the scene to prevent crashes
        try:
            pmc.newFile()
        except RuntimeError as e:
            logger.error("Could not close scene!")
            logger.error(e)
            return False

        # Creating Backup file
        try:
            shutil.copy(filePath, bakPath)
        except IOError as e:
            logger.error("Could not create backup file!")
            logger.error(e)
            return False
        else:
            logger.info("Created Backup file")

        # transfering file content, line by line
        try:
            with open(bakPath, "r") as srcFile:
                with open(filePath, "w") as trgFile:
                    for line in srcFile:
                        if 'fileInfo "license" "student";' in line:
                            logger.info("Student License String found")
                            trgFile.write('fileInfo "license" "education";')
                        else:
                            trgFile.write(line)
        except IOError as e:
            logger.error("An Error occurred while reading/writing the scene file")
            logger.error(e)
            return False

        # Reopening current scene
        try:
            pmc.openFile(filePath)
        except IOError as e:
            logger.error("Could not reopen current scene!")
            logger.error(e)
            return False
        except RuntimeError as e:
            logger.error(e)
            return False

        return True

    def close_scene(self):
        ''' Closes the scene, without changing any meta '''
        logger.debug("Closing Scene")
        try:
            pmc.newFile()
            return True
        except RuntimeError as e:
            logger.error("Could not close scene!")
            logger.error(e)
            return False
