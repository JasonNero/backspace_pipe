import pymel.core as pmc
import re
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import getpass
import time
from sets import Set

from backspace_pipe import slack_tools, logging_control, scene_control


# ### ### ### ### ### GLOABL VARS ### ### ### ### ### ###

last_incremental_save = ""
logger = logging_control.get_logger()


# ### ### ### ### ### ### COMMON ### ### ### ### ### ###

def toggle_wait_cursor():
    logger.debug("Toggle wait cursor")
    current_state = pmc.waitCursor(query=True, state=True)
    pmc.waitCursor(state=not current_state)
    return True


# ### ### ### ### ### ### MOD SETUP ### ### ### ### ### ###

def save_on_setup():
    logger.debug("Save on Setup")
    try:
        result = scene_control.get_instance().save()
        return result
    except RuntimeError as e:
        logger.error(e)
        logger.error("Could not save file!")
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
    error_counter = 0

    for node in unknown_nodes:
        logger.info("Deleting Node: \t{}".format(node))
        try:
            pmc.delete(node)
        except RuntimeError as e:
            logger.error("Deletion Error: {}".format(e))
            error_counter += 1

    if error_counter == 0:
        return True
    else:
        return False


def del_displaylayers():
    logger.debug("Delete displayLayers")

    displayLayers = pmc.ls(type="displayLayer")
    error_counter = 0

    for layer in displayLayers:
        if ("defaultLayer" in repr(layer)):
            # Ignore and continue with next layer
            continue
        else:
            logger.info("Deleting Layer: \t{}".format(layer))
            try:
                pmc.delete(layer)
            except RuntimeError as e:
                logger.error("Deletion Error: {}".format(e))
                error_counter += 1

    if error_counter == 0:
        return True
    else:
        return False


def del_all_history():
    logger.debug("Delete ALL history")

    try:
        pmc.mel.eval("DeleteAllHistory;")
        return True
    except RuntimeError as e:
        logger.error(e)
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

    error_counter = 0

    for node in non_unique_nodes:
        short_node_name = node.shortName()

        base_node_name_matches = re_base_node_name.search(short_node_name)
        base_node_name = base_node_name_matches.group(0)

        suffix_matches = re_suffix.search(base_node_name)
        suffix = suffix_matches.group(0) if suffix_matches else base_node_name

        # Appending a #, Maya will automatically insert the next free number (pCube# -> pCube1)
        optimal_node_name = suffix + '#'

        try:
            node.rename(optimal_node_name)
        except RuntimeError as e:
            logger.error("Could not rename node {} to {}".format(short_node_name, optimal_node_name))
            logger.error(e)
            error_counter += 1
        else:
            new_node_name = node.shortName()
            logger.info("Renamed node {} to {}".format(short_node_name, new_node_name))

    if error_counter == 0:
        return True
    else:
        return False


def assure_shape_names():
    logger.debug("Assure Shape Names")

    all_transforms = pmc.ls(type='transform')

    error_counter = 0

    for transf in all_transforms:
        shapes = transf.listRelatives(shapes=True)

        for shape in shapes:
            current_shape_name = shape.shortName()
            re_incr = re.compile(r"\d*$")

            optimal_shape_name = re_incr.split(transf.shortName())[0] + "Shape" + re_incr.search(transf.shortName()).group(0)

            if(current_shape_name != optimal_shape_name):
                try:
                    shape.rename(optimal_shape_name)
                except RuntimeError:
                    logger.error("Could not rename node {} to {}".format(current_shape_name, optimal_shape_name))
                    error_counter += 1
                else:
                    new_shape_name = shape.shortName()
                    logger.info("Renamed shape {} to {}".format(current_shape_name, new_shape_name))

    if error_counter == 0:
        return True
    else:
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


# ### ### ### ### ### ### MOD PUBLISH ### ### ### ### ### ###

def fit_view():
    logger.debug("Fit View")
    pmc.select(clear=True)
    pmc.viewFit(all=True)
    return True


def incremental_save():
    logger.debug("INCREMETAL SAVE")

    try:
        return scene_control.get_instance().save_incr(comment="INCREMETAL")
    except RuntimeError as e:
        logger.error("Could not save file!")
        logger.error(e)
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

    error_counter = 0
    if len(ref_set) > 0:
        for ref in ref_set:
            logger.info("Importing Reference: {}".format(ref.refNode))
            try:
                ref.importContents()
            except RuntimeError as e:
                logger.error("Could not import Reference {}".format(ref.refNode))
                logger.error(e)
                error_counter += 1

    create_refsToImport_set()

    if error_counter == 0:
        return True
    else:
        return False


def rem_all_refs():
    logger.debug("Removing all References")

    error_counter = 0

    for ref in pmc.iterReferences():
        logger.info("Removing Reference: {}".format(ref.refNode))
        try:
            ref.remove()
        except RuntimeError as e:
            logger.error("Could not remove Reference {}".format(ref.refNode))
            logger.error(e)
            error_counter += 1

    if error_counter == 0:
        return True
    else:
        return False


def del_delOnPub_set():
    logger.debug("Delete deleteOnPublish Set")

    maya_set_ls = pmc.ls("deleteOnPublish")

    if len(maya_set_ls) == 0:
        logger.info("deleteOnPublish Set is nonexistent")
        return True

    maya_set = maya_set_ls[0]
    nodes = maya_set.elements()

    error_counter = 0

    for node in nodes:
        logger.info("Deleting: {}".format(node))

        try:
            pmc.delete(node)
        except RuntimeError as e:
            logger.error("Could not delete Node {}".format(node))
            logger.error(e)
            error_counter += 1

    create_delOnPub_set()

    if error_counter == 0:
        return True
    else:
        return False


def assure_lambert1():
    logger.debug("Assure lambert1")
    shapes = pmc.ls(geometry=True)
    pmc.sets("initialShadingGroup", forceElement=shapes)
    return True


def delete_unused_nodes():
    logger.debug("Deleting unused nodes")
    pmc.mel.eval("MLdeleteUnused;")
    return True


def publish():
    logger.debug("PUBLISH")

    try:
        return scene_control.get_instance().publish()
    except RuntimeError as e:
        logger.error("Could not save file!")
        logger.error(e)
        return False


def slack_publish_notification():
    logger.debug("Slack Publish Notification")
    # Refresh viewport
    pmc.refresh(force=True)

    # Grab the last active 3d viewport
    view = omui.M3dView.active3dView()
    # Enable Alpha
    view.setColorMask(1, 1, 1, 1)

    # read the color buffer from the view, and save the MImage to disk
    image = om.MImage()
    view.readColorBuffer(image, True)

    scene_path = pmc.sceneName()
    file_path = scene_path.splitext()[0] + ".png"

    try:
        image.writeToFile(file_path, 'png')
    except (IOError, RuntimeError) as e:
        logger.error("Could not save png Thumbnail!")
        logger.error(e)
        return False

    re_incr = re.compile(r"_\d+")

    curr_asset = re_incr.split(scene_path.name)[0]
    user = getpass.getuser()
    date_str = time.strftime("%Y_%m_%d")

    initial_comment = "*{asset}* has been published by _{user}_ with the comment _'{comment}'_".format(asset=curr_asset, user=user, comment=scene_control.get_instance().meta.comment)
    file_name = "{date}_{asset}".format(date=date_str, asset=curr_asset)

    slack_tools.send_file(channels="publish", file_path=file_path, file_name=file_name, file_type="png", title=file_name, initial_comment=initial_comment)

    return True


def close_scene():
    logger.debug("Close Scene")
    return scene_control.get_instance().close_scene()


def del_maya_lic_string():
    logger.debug("Delete Maya Lic String")
    return scene_control.get_instance().del_maya_lic_string()


def open_last_increment():
    logger.debug("Open last increment")
    return scene_control.get_instance().load_latest_incr()
