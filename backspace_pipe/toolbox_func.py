import pymel.core as pmc
import re
import logging
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
import getpass
import time
import shutil
import sys
from sets import Set

from backspace_pipe import slack_tools


# ### ### ### ### ### # GLOABL VARS # ### ### ### ### ### ###

last_incremental_save = ""
logging_level = logging.DEBUG


# ### ### ### ### ### ### LOGGING ### ### ### ### ### ###

# Create Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

# Prevent Call to Maya Logger
logger.propagate = False

# Remove old handlers
for hndl in logger.handlers:
    logger.removeHandler(hndl)

# # Custom Stream Handler
# stream_handler = logging.StreamHandler()

# # Maya Stream Handler
# maya_handler = maya.utils.MayaGuiLogHandler()

# Output Window Handler
out_win_handler = logging.StreamHandler(sys.__stdout__)

# Create and apply Formatter to Handler
formatter = logging.Formatter('pipe:\t\t%(levelname)-8s - %(message)s')
out_win_handler.setFormatter(formatter)

# Add Handler to Logger
logger.addHandler(out_win_handler)


# ### ### ### ### ### ### COMMON ### ### ### ### ### ###

def get_logger():
    return logger


def toggle_wait_cursor():
    logger.debug("Toggle wait cursor")
    current_state = pmc.waitCursor(query=True, state=True)
    pmc.waitCursor(state=not current_state)
    return True


# ### ### ### ### ### ### SETUP ### ### ### ### ### ###

def save_on_setup():
    logger.debug("Save on Setup")
    try:
        pmc.saveFile()
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def create_delOnPub_set():
    logger.debug("Create delOnPub Set")

    if(len(pmc.ls("deleteOnPublish")) == 0):
        pmc.sets(name="deleteOnPublish", empty=True)
    return True


def create_refsToImport_set():
    logger.debug("Create refsToImport Set")

    if(len(pmc.ls("refsToImport")) == 0):
        pmc.sets(name="refsToImport", empty=True)
    return True


def del_unknown_dag():
    logger.debug("Delete unknown DAG nodes")

    unknown_nodes = pmc.ls(type="unknown")

    try:
        for node in unknown_nodes:
            logger.info("Deleting Node: \t{}".format(node))
            pmc.delete(node)
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def del_displaylayers():
    logger.debug("Delete displayLayers")

    displayLayers = pmc.ls(type="displayLayer")

    try:
        for layer in displayLayers:
            if ("defaultLayer" in repr(layer)):
                # Ignore and continue with next layer
                continue
            else:
                logger.info("Deleting Layer: \t{}".format(layer))
                pmc.delete(layer)
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def del_all_history():
    logger.debug("Delete ALL history")

    try:
        pmc.mel.eval("DeleteAllHistory;")
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def assure_unique_naming():
    logger.debug("Assure Unique Naming")

    # Exclude shapes, as they will be renamed automatically if named after the transform
    all_nodes = pmc.ls(shortNames=True, excludeType='shape')
    non_unique_nodes = [node for node in all_nodes if "|" in node.shortName()]

    # Regular Expression: 0 or more times no '|' at the end of the string
    re_base_node_name = re.compile(r'[^|]*$')

    # Regular Expression: 0 or more times a character then no number
    re_suffix = re.compile(r'.*[^0-9]')

    try:
        for node in non_unique_nodes:
            short_node_name = node.shortName()

            base_node_name_matches = re_base_node_name.search(short_node_name)
            base_node_name = base_node_name_matches.group(0)

            suffix_matches = re_suffix.search(base_node_name)
            suffix = suffix_matches.group(0) if suffix_matches else base_node_name

            # Appending a #, Maya will automatically insert the next free number (pCube# -> pCube1)
            new_node_name = suffix + '#'
            node.rename(new_node_name)
            new_node_name = node.shortName()

            logger.info("Renamed {} to {}".format(short_node_name, new_node_name))
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def assure_shape_names():
    logger.debug("Assure Shape Names")

    all_transforms = pmc.ls(type='transform')

    try:
        for transf in all_transforms:
            shapes = transf.listRelatives(shapes=True)

            for shape in shapes:
                current_shape_name = shape.shortName()
                re_incr = re.compile(r"\d*$")

                optimal_shape_name = re_incr.split(transf.shortName())[0] + "Shape" + re_incr.search(transf.shortName()).group(0)

                if(current_shape_name != optimal_shape_name):
                    logger.info("Renaming shape to match transform: {} to {}".format(current_shape_name, optimal_shape_name))
                    shape.rename(optimal_shape_name)

        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def mesh_check():
    logger.debug("Mesh Check")

    all_shapes = pmc.ls(shapes=True)

    check_results = []

    for shape in all_shapes:
        inv_edges = pmc.polyInfo(shape, ie=True)
        inv_verts = pmc.polyInfo(shape, iv=True)
        lamina_faces = pmc.polyInfo(shape, lf=True)
        nonm_edges = pmc.polyInfo(shape, nme=True)
        nonm_verts = pmc.polyInfo(shape, nmv=True)

        error_list = [shape, inv_edges, inv_verts, lamina_faces, nonm_edges, nonm_verts]

        if error_list.count(None) < 5:
            check_results.append(error_list)

    return True


# ### ### ### ### ### ### PUBLISH ### ### ### ### ### ###

def fit_view():
    logger.debug("Fit View")
    pmc.viewFit(all=True)
    return True


def incremental_save():
    logger.debug("INCREMETAL SAVE")

    curr_path = pmc.sceneName()
    curr_name, curr_ext = curr_path.name.splitext()

    re_incr = re.compile(r"_\d+")
    match = re_incr.search(curr_name)

    if match is None:
        logger.warning("Please check filename format: 'your_asset_name_XX_optional_comment' with XX being an integer (padding can vary)!")
        return False

    curr_asset = re_incr.split(curr_name)[0]

    curr_incr_str = match.group(0).replace("_", "")

    new_incr_int = int(curr_incr_str) + 1

    incr_padding = len(curr_incr_str)

    new_incr_str = "_{num:0{width}d}".format(num=new_incr_int, width=incr_padding)

    new_path = pmc.Path(curr_path.parent + "/" + curr_asset + new_incr_str + curr_ext)

    logger.info("Increment: {}".format(new_path))

    try:
        pmc.saveAs(new_path)
        global last_incremental_save
        last_incremental_save = new_path
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def import_refs_set():
    logger.debug("Import Refs Set")

    maya_set_ls = pmc.ls("refsToImport")

    if len(maya_set_ls) == 0:
        logger.info("refsToImport Set is nonexistent")
        return True

    maya_set = maya_set_ls[0]
    elements = maya_set.elements()
    ref_set = Set([])

    for e in elements:
        if e.isReferenced():
            e_ref = e.referenceFile()

            # Getting all parents of the FileReference Node
            parents = [e_ref]
            while parents[-1].parent() is not None:
                parents.append(parents[-1].parent())

            # Reversing List in order for importContents() to work and adding it to the Set
            parents.reverse()
            for ref in parents:
                ref_set.add(ref)
        else:
            maya_set.remove(e)

    try:
        if len(ref_set) > 0:
            for ref in ref_set:
                logger.info("Importing Reference: {}".format(ref))
                ref.importContents()

        create_refsToImport_set()
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def rem_all_refs():
    logger.debug("Removing all References")

    try:
        for ref in pmc.iterReferences():
            logger.info("Removing Reference: {}".format(ref))
            ref.remove()
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def del_delOnPub_set():
    logger.debug("Delete deleteOnPublish Set")

    maya_set_ls = pmc.ls("deleteOnPublish")

    if len(maya_set_ls) == 0:
        logger.info("deleteOnPublish Set is nonexistent")
        return True

    maya_set = maya_set_ls[0]
    elements = maya_set.elements()

    try:
        for e in elements:
            logger.info("Deleting: {}".format(e))
            pmc.delete(e)
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False

    create_delOnPub_set()

    return True


def assure_lambert1():
    logger.debug("Assure lambert1")
    shapes = pmc.ls(geometry=True)
    pmc.sets("initialShadingGroup", forceElement=shapes)

    # materials_with_sg = pmc.ls(type="shadingEngine", materials=True)
    # pmc.delete(materials_with_sg)
    return True


def delete_unused_nodes():
    logger.debug("Deleting unused nodes")
    pmc.mel.eval("MLdeleteUnused;")
    return True


def publish():
    logger.debug("PUBLISH")

    curr_path = pmc.sceneName()
    curr_name, curr_ext = curr_path.name.splitext()

    re_incr = re.compile(r"_\d+")
    curr_asset = re_incr.split(curr_name)[0]

    new_path = pmc.Path(curr_path.parent.parent + "/" + curr_asset + "_REF" + curr_ext)

    logger.info("Publishing File: {}".format(new_path))

    try:
        pmc.saveAs(new_path)
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def slack_publish_notification():
    logger.debug("Slack Publish Notification")
    # Refresh viewport
    pmc.refresh(force=True)

    # Grab the last active 3d viewport
    view = apiUI.M3dView.active3dView()
    # Enable Alpha
    view.setColorMask(1, 1, 1, 1)

    # read the color buffer from the view, and save the MImage to disk
    image = api.MImage()
    view.readColorBuffer(image, True)

    scene_path = pmc.sceneName()
    file_path = scene_path.splitext()[0] + ".png"

    try:
        image.writeToFile(file_path, 'png')
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False

    re_incr = re.compile(r"_\d+")

    curr_asset = re_incr.split(scene_path.name)[0]
    user = getpass.getuser()
    date_str = time.strftime("%Y_%m_%d")

    initial_comment = "*{asset}* has been published by _{user}_".format(asset=curr_asset, user=user)
    file_name = "{date}_{asset}".format(date=date_str, asset=curr_asset)

    slack_tools.send_file(channels="publish", file_path=file_path, file_name=file_name, file_type="png", title=file_name, initial_comment=initial_comment)

    # Maybe just keep the screenshot?
    # os.remove(file_path)

    return True


def close_scene():
    logger.debug("Closing Scene")
    try:
        pmc.newFile()
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False


def del_maya_lic_string():
    logger.debug("Deleting Maya License String")

    filePath = pmc.sceneName()
    bakPath = filePath + ".bak"

    # Closing the file to prevent crashes
    pmc.newFile()

    # Creating Backup file
    shutil.copy(filePath, bakPath)

    try:
        with open(bakPath, "r") as srcFile:
            with open(filePath, "w") as trgFile:
                for line in srcFile:
                    if 'fileInfo "license" "student";' in line:
                        logger.info("Student License String found")
                    else:
                        trgFile.write(line)
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False

    pmc.openFile(filePath)

    return True


def open_last_increment():
    logger.debug("Open last increment")

    # ####### Programmatical Approach - save for later?
    # curr_path = pmc.sceneName()

    # re_incr = re.compile(r"_\d+")

    # highest_incr_int = 0
    # highest_incr_path = ""

    # for root, subdirs, files in os.walk(curr_path.parent):
    #     for file in files:
    #         match = re_incr.search(file)

    #         if match is None:
    #             continue

    #         logger.info(os.path.join(root, file))

    #         curr_incr_int = int(match.group(0).replace("_", ""))

    #         if curr_incr_int > highest_incr_int:
    #             highest_incr_int = curr_incr_int
    #             highest_incr_path = os.path.join(root, file)

    # recent_files = pmc.optionVar.get("RecentFilesList")
    ########

    try:
        pmc.openFile(last_incremental_save)
        return True
    except Exception as e:
        logger.error("An Exception occured, please contact Jason to fix this!")
        logger.exception(e)
        return False
