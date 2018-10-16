import pymel.core as pmc

hotkeys_setup = False
port_setup = False
pipe_path = pmc.Path(__file__).parent.parent
maya_project_path = pmc.Path(__file__).splitdrive()[0] / "/04_workflow"

# Set Project
pmc.mel.eval('setProject "' + maya_project_path + '"')

# Port Setup
if not port_setup:
    try:
        pmc.commandPort(name=":7002", sourceType="python")
    except RuntimeError as e:
        pmc.warning(e)

    port_setup = True

# Hotkey Setup
if not hotkeys_setup:
    if pmc.hotkeySet("BackspaceHotkeys", query=True, exists=True):
        pmc.hotkeySet("BackspaceHotkeys", edit=True, current=True)
    else:
        pmc.hotkeySet(edit=True, ip=pipe_path + "/BackspaceHotkeys.mhk")

    hotkeys_setup = True
