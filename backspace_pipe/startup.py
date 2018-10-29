import maya.cmds as cmds

hotkeys_setup = False
port_setup = False
project_setup = False


# This method is being called by __init__.py on Maya Startup
def startup():
    import backspace_pipe.logging_control as logging_control
    logger = logging_control.get_logger()
    logger.info("Backspace Logger Loaded!")

    if not cmds.about(batch=True):
        logger.info("Backspace Pipe not in Batch Mode")
        cmds.evalDeferred("import backspace_pipe.startup as startup; startup.startup_deferred()")
    else:
        logger.info("Backspace Pipe in Batch Mode")


# This method is being called deferred, because pymel is not loaded yet
def startup_deferred():
    import pymel.core as pmc

    pipe_path = pmc.Path(__file__).parent.parent
    maya_project_path = pmc.Path(__file__).splitdrive()[0] / "/04_workflow"

    # DragnDrop Feature
    dragndrop_script_path = pipe_path / "backspace_pipe" / "mel" / "performFileDropAction.mel"
    pmc.mel.evalDeferred('source "{}"'.format(dragndrop_script_path.replace("\\", "/")))

    # Set Project
    global project_setup
    if not project_setup:
        pmc.mel.eval('setProject "{}"'.format(maya_project_path))

    # Port Setup
    global port_setup
    if not port_setup:
        try:
            pmc.commandPort(name=":7002", sourceType="python")
        except RuntimeError as e:
            pmc.warning(e)

        port_setup = True

    # Hotkey Setup
    global hotkeys_setup
    if not hotkeys_setup:
        if pmc.hotkeySet("BackspaceHotkeys", query=True, exists=True):
            pmc.hotkeySet("BackspaceHotkeys", edit=True, current=True)
        else:
            pmc.hotkeySet(edit=True, ip=pipe_path + "/BackspaceHotkeys.mhk")

        hotkeys_setup = True
