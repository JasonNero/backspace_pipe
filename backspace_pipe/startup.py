import maya.cmds as cmds

def startup():
    import backspace_pipe.logging_control as logging_control
    logger = logging_control.get_logger()
    logger.info("Backspace Pipe Loaded!")
    cmds.evalDeferred("import backspace_pipe.core")

    try:
        cmds.commandPort(name=":7002", close=True)
    except:
        cmds.warning("Could not close port 7002")

    try:
        cmds.commandPort(name=":7002", sourceType="python")
    except:
        cmds.warning("Could not open port 7002")
