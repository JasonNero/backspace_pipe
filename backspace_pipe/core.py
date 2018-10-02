from backspace_pipe.scene_control import SceneControl
import pymel.core as pmc

hotkeys_setup = False
pipe_path = pmc.Path(__file__).parent.parent

# Some basic functionality
scene_controller = SceneControl()

if not hotkeys_setup:
    if pmc.hotkeySet("BackspaceHotkeys", query=True, exists=True):
        pmc.hotkeySet("BackspaceHotkeys", edit=True, current=True)
    else:
        pmc.hotkeySet(edit=True, ip=pipe_path + "/BackspaceHotkeys.mhk")

        # # OPEN
        # if pmc.runTimeCommand("backspace_open_runtime", exists=True):
        #     print("Command backspace_open has already been added")
        # else:
        #     pmc.runTimeCommand(
        #         "backspace_open_runtime", ann="Backspace Open", category="Custom Scripts",
        #         command="import backspace_pipe.core as core; core.scene_controller.load_dialogue()", showInHotkeyEditor=1)
        #     pmc.nameCommand("backspace_open", ann="Backspace", command="backspace_open_runtime")
        # # pmc.hotkey(keyShortcut='o', ctrlModifier=True, name="backspace_open")

        # # SAVE
        # if pmc.runTimeCommand("backspace_save_runtime", exists=True):
        #     print("Command backspace_save has already been added")
        # else:
        #     pmc.runTimeCommand(
        #         "backspace_save_runtime", ann="Backspace Save", category="Custom Scripts",
        #         command="import backspace_pipe.core as core; core.scene_controller.save()", showInHotkeyEditor=1)
        #     pmc.nameCommand("backspace_save", ann="Backspace", command="backspace_save_runtime")
        # # pmc.hotkey(keyShortcut='s', ctrlModifier=True, name="backspace_save")

        # # SAVE AS
        # if pmc.runTimeCommand("backspace_save_as_runtime", exists=True):
        #     print("Command backspace_save_as has already been added")
        # else:
        #     pmc.runTimeCommand(
        #         "backspace_save_as_runtime", ann="Backspace Save As", category="Custom Scripts",
        #         command="import backspace_pipe.core as core; core.scene_controller.save_dialogue()", showInHotkeyEditor=1)
        #     pmc.nameCommand("backspace_save_as", ann="Backspace", command="backspace_save_as_runtime")
        # # pmc.hotkey(keyShortcut='s', ctrlModifier=True, shiftModifier=True, name="backspace_save_as")

        # # INCREMENT
        # if pmc.runTimeCommand("backspace_incr_runtime", exists=True):
        #     print("Command backspace_incr has already been added")
        # else:
        #     pmc.runTimeCommand(
        #         "backspace_incr_runtime", ann="Backspace Increment", category="Custom Scripts",
        #         command="import backspace_pipe.core as core; core.scene_controller.save_incr()", showInHotkeyEditor=1)
        #     pmc.nameCommand("backspace_incr", ann="Backspace", command="backspace_incr_runtime")
        # # pmc.hotkey(keyShortcut='s', ctrlModifier=True, altModifier=True, name="backspace_incr")

    hotkeys_setup = True
