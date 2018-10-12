import maya.cmds as cmds

# This method is being called by __init__.py on Maya Startup
def startup():
    import backspace_pipe.logging_control as logging_control
    logger = logging_control.get_logger()
    logger.info("Backspace Pipe Loaded!")

    if not cmds.about(batch=True):
        cmds.evalDeferred("import backspace_pipe.core")
