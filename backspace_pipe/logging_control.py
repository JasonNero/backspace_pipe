import logging
import sys
import os

from backspace_pipe.constants import Log_Mode

standard_logging_level = logging.DEBUG
standard_logging_mode = Log_Mode.MAYA_WINDOW

_initialized = False
logger = None
formatter = None


def get_logger():
    return logger


def add_handler(logging_mode, widget=None):
    if logging_mode == Log_Mode.MAYA_WINDOW:
        handler = logging.StreamHandler(sys.__stdout__)
    elif logging_mode == Log_Mode.MAYA_STREAM:
        import maya
        handler = maya.utils.MayaGuiLogHandler()
    elif logging_mode == Log_Mode.CUSTOM_STREAM:
        handler = logging.StreamHandler()
    elif logging_mode == Log_Mode.QTEXT:
        handler = QTextHandler(widget)
    elif logging_mode == Log_Mode.FILE:
        # Saving Log file to Desktop
        file_path = os.path.abspath(os.path.join(os.environ["HOMEPATH"], "Desktop\\backspace.log"))
        handler = logging.FileHandler(file_path)
    else:
        return

    # apply Formatter to Handler
    handler.setFormatter(formatter)

    # Add Handler to Logger
    logger.addHandler(handler)


# Custom StreamHandler appending msg to Widget text
class QTextHandler(logging.StreamHandler):
    def __init__(self, widget):
        logging.StreamHandler.__init__(self)
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        print(msg)
        # Strip trailing whitespace and make text html conform
        msg = msg.rstrip()
        msg = msg.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        msg = msg.replace(" ", "&nbsp;")
        print(msg)
        level = record.levelno

        if level == logging.DEBUG:
            color = "gray"
        elif level == logging.INFO:
            color = "white"
        elif level == logging.WARNING:
            color = "yellow"
        elif level == logging.ERROR:
            color = "red"
        elif level == logging.CRITICAL:
            color = "darkred"

        html = "<font color='{color}'>{msg}</font>".format(color=color, msg=msg)
        print(html)
        self.widget.appendHtml(html)


# INIT
if not _initialized:
    # Create Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(standard_logging_level)

    # Prevent Call to Maya Logger
    logger.propagate = False

    # Remove old handlers
    for hndl in logger.handlers:
        logger.removeHandler(hndl)

    # Create Formatter
    formatter = logging.Formatter('pipe:\t%(levelname)-8s - %(message)s')

    add_handler(standard_logging_mode)

    _initialized = True
