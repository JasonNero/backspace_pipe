import pymel.core as pmc
import re
import os
from backspace_pipe.meta import MetaData
from backspace_pipe import logging_control

logger = logging_control.get_logger()


class SceneControl():
    meta = None
    incr_padding = 2

    def __init__(self):
        self.meta = MetaData()

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

    def load_latest_incr(self):
        ''' Load latest increment of current Asset. '''
        re_incr = re.compile(r"_(\d+)(_\w+)?(.ma$)")

        asset_path = pmc.Path(self.meta.current_file).parent

        logger.error(asset_path)

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
            logger.error(e)
            confirmation = pmc.confirmDialog(
                title='Confirm', message="{}Force Open?".format(e), button=['Yes', 'No'],
                defaultButton='Yes', cancelButton='No', dismissString='No')
            if confirmation == 'Yes':
                pmc.openFile(file, force=True)
        self.meta = MetaData(fromFile=True)
        # self.meta.dump_to_log()
        return True

    # # BIG TODO: Wie gehe ich mit neuen Assets um?
    # def setup_save(self, asset_name, comment=None):
    #     ''' First Save of an Asset Setup.'''
    #     self.meta = MetaData()
    #     self.meta.asset = asset_name
    #     workspace_dir = pmc.workspace.getPath()
    #     pmc.saveAs()

    def save_dialogue(self):
        selected_file = pmc.fileDialog2(
            fileMode=0, fileFilter="*.ma *.mb", dialogStyle=2,
            dir=pmc.workspace.path / pmc.workspace.fileRules["mayaAscii"])
        if selected_file:
            self.save_as(file=selected_file[0])

    def save(self, comment=None):
        ''' Wraps pymel save scene according to pipeline definitions. '''
        # Finalize and save MetaData for current scene
        if not comment:
            result = pmc.promptDialog(
                title="Comment", message="Enter Comment:", button=["OK", "Cancel"],
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel")
            if result == "OK":
                comment = pmc.promptDialog(query=True, text=True)

        self.meta.update()
        self.meta.comment = comment
        self.meta.save_metafile()

        logger.info("Saving file...")
        # self.meta.dump_to_log()
        pmc.saveFile()
        return True

    def save_as(self, file, comment=None):
        ''' Wraps pymel saveAs scene according to pipeline definitions. '''

        # # Finalize and save MetaData for current scene
        # self.meta.update()
        # self.meta.comment = comment
        # self.meta.save_metafile()

        if not comment:
            result = pmc.promptDialog(
                title="Comment", message="Enter Comment:", button=["OK", "Cancel"],
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel")
            if result == "OK":
                comment = pmc.promptDialog(query=True, text=True)

        recent_file = pmc.sceneName()
        logger.info("Saving as {} ...".format(file))
        # self.meta.dump_to_log()
        pmc.saveAs(file)

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
        match = re_incr.search(curr_name)

        if match is None:
            logger.warning("Please check filename format: 'your_asset_name_XX_optional_comment.ma'!")
            return False

        curr_asset = re_incr.split(curr_name)[0]

        curr_incr_str = match.group(0).replace("_", "")

        new_incr_int = int(curr_incr_str) + 1

        # "_{num:0{width}d}" creates the increment suffix with leading zeroes
        new_incr_str = "_{num:0{width}d}".format(num=new_incr_int, width=self.incr_padding)

        incr_file = pmc.Path(curr_path.parent + "/" + curr_asset + new_incr_str + curr_ext)

        self.save_as(incr_file, comment)
        return True

    def publish(self, comment=None):
        ''' Publish scene with comment. '''
        curr_path = pmc.sceneName()
        curr_name, curr_ext = curr_path.name.splitext()

        re_incr = re.compile(r"_\d+")
        curr_asset = re_incr.split(curr_name)[0]

        new_path = pmc.Path(curr_path.parent.parent + "/" + curr_asset + "_REF" + curr_ext)

        self.save_as(new_path, comment)
        return True
