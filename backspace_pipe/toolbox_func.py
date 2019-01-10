import pymel.core as pmc
import re
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import getpass
import time
from sets import Set

from backspace_pipe import slack_tools, logging_control, scene_control, dep_switcher


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


def check_nonuniform_scale():
    logger.debug("Checking for Non-Uniformly Scaled Shapes and Transforms")
    nonuniform_scale = []

    for node in pmc.ls(transforms=True):
        scale_values = node.scale.get()
        if not scale_values.count(scale_values[0]) == 3:
            nonuniform_scale.append(node)

    if len(nonuniform_scale) != 0:
        logger.error("Found non-uniform scale on following shapes:")
        for item in nonuniform_scale:
            logger.error(item)

        return False
    else:
        return True


def delete_nondefault_cameras():
    default_cams = ["frontShape", "sideShape", "topShape", "perspShape"]

    for cam in pmc.ls(cameras=True):
        if cam not in default_cams:
            cam_transf = cam.getTransform()
            pmc.delete(cam_transf)

    return True


def assure_lambert1():
    logger.debug("Assure lambert1")
    shapes = pmc.ls(geometry=True)
    pmc.sets("initialShadingGroup", forceElement=shapes)
    return True


def delete_unused_nodes():
    logger.debug("Deleting unused nodes")
    pmc.mel.eval("MLdeleteUnused;")
    return True


def delete_sets():
    logger.debug("Deleting Pipeline Sets")
    pmc.delete(pmc.ls("deleteOnPublish"))
    pmc.delete(pmc.ls("refsToImport"))
    return True


def unsmooth_all():
    logger.debug("Unsmooth")
    all_geo = pmc.ls(type='mesh')
    pmc.displaySmoothness(all_geo, du=0, dv=0, pw=4, ps=1, po=1)
    return True


def update_dep():
    logger.debug("Updating all MDL References to SHD")

    return dep_switcher.switch(curr_dep="MDL", new_dep="ASS", replace=False, grouped=True)


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


# ### ### ### ### ### ### SHD SETUP ### ### ### ### ### ###

def is_mdl_referenced():
    logger.debug("Check for MDL Reference")
    asset_base = pmc.sceneName().parent.parent
    asset_name = scene_control.get_instance().meta.asset.replace("_SHD", "")
    mdl_ref_path = asset_base + "/" + asset_name + "_MDL_REF.ma"

    print(mdl_ref_path)
    print("\n")

    mdl_ref_found = False

    for ref in pmc.iterReferences():
        if ref.path == mdl_ref_path:
            mdl_ref_found = True
            break

    return mdl_ref_found


def ref_shading_lightset():
    logger.debug("Create Reference for Lightset")

    try:
        pmc.createReference("M:/04_workflow/scenes/assets/locations/shadingSetup/Maya/shadingSetup_REF.ma", ns="shadingSetup")
    except RuntimeError as e:
        logger.error(e)
        return False

    return True


def set_default_aiSubdiv():
    logger.debug("Setting Default aiSubdiv Settings")

    for shape in pmc.ls(type="mesh"):
        shape.setAttr("aiSubdivType", 1)
        shape.setAttr("aiSubdivIterations", 2)
        shape.setAttr("aiSubdivUvSmoothing", 1)

    return True


def set_default_aiVisibility():
    logger.debug("Setting Default aiVisibility Settings")

    for shape in pmc.ls(type="mesh"):
        shape.setAttr("primaryVisibility", 1)
        shape.setAttr("castsShadows", 1)
        shape.setAttr("aiVisibleInDiffuseReflection", 1)
        shape.setAttr("aiVisibleInSpecularReflection", 1)
        shape.setAttr("aiVisibleInDiffuseTransmission", 1)
        shape.setAttr("aiVisibleInSpecularTransmission", 1)
        shape.setAttr("aiVisibleInVolume", 1)
        shape.setAttr("aiSelfShadows", 1)

    return True


# ### ### ### ### ### ### SHD PUBLISH ### ### ### ### ### ###

def check_subref_dep():
    logger.debug("Checking if all SubReferences are SHD files")

    faulty_refs = []

    for ref in pmc.iterReferences():
        # # Check top nodes aswell
        # ref_name_trimmed = str(ref.refNode)
        # if "MDL" in ref_name_trimmed:
        #     faulty_refs.append(ref.refNode)

        for subref in ref.subReferences():
            subref_name_trimmed = "".join(subref.split(":")[1:])
            if "MDL" in subref_name_trimmed:
                faulty_refs.append(subref)

    if len(faulty_refs) == 0:
        return True
    else:
        logger.error("The following Refs seems to be faulty:")
        for ref in faulty_refs:
            logger.error(ref)
        return False


def check_lambert():
    logger.debug("Checking for meshes with lambert1 assigned")

    init_SG = pmc.ls("initialShadingGroup")[0]

    if len(init_SG) == 0:
        return True
    else:
        logger.error("Following Shapes have lambert1 assigned!")
        for shape in pmc.sets(init_SG, query=True):
            logger.error(shape)

        return False


def close_ai_view():
    logger.debug("Closing Arnold IPR")
    try:
        pmc.mel.eval('workspaceControl -edit -cl "ArnoldRenderView";')
    except RuntimeError as e:
        logger.info(e)

    return True


def check_input_paths():
    ''' Checking for absolute or unresolved paths '''
    logger.debug("Checking for invalid File Paths")

    success = True

    # Update FilePathEditor
    pmc.filePathEditor(refresh=True)

    # Unresolved Files
    unresolved_list = pmc.filePathEditor(query=True, listFiles="", unresolved=True)
    if unresolved_list:
        logger.warning("Unresolved Files Found:")
        success = False
        for f in unresolved_list:
            logger.warning(".. {}".format(f))

    # Non relative paths
    base_path = pmc.workspace.path
    file_dirs = pmc.filePathEditor(query=True, listDirectories="")

    non_relative_dirs = []
    if file_dirs:
        for directory in file_dirs:
            if base_path not in directory:
                non_relative_dirs.append(directory)

        if len(non_relative_dirs) != 0:
            success = False
            logger.warning("Files outside the project found:")
            for directory in non_relative_dirs:
                logger.warning(".. {}".format(directory))

    return success


def rem_unloaded_refs():
    logger.debug("Removing unloaded References")

    success = True
    for ref in pmc.iterReferences():
        if not ref.isLoaded():
            try:
                ref.remove()
            except RuntimeError as e:
                logger.error("Could not remove ref: {}".format(ref.namespace))
                logger.error(e)
                success = False

    return success


def deref_shading_lightset():
    logger.debug("Removing Shading Lightset")

    for ref in pmc.iterReferences():
        if "shadingSetup" in ref.namespace:
            try:
                ref.remove()
                return True
            except RuntimeError as e:
                logger.error(e)
                return False

    # If the loop runs trough and no lightset is found, consider it an error
    return False


def rem_ref_edits():
    logger.debug("Removing Reference Edits")
    parameters = ('.translate', '.rotate', '.scale')

    success = True

    for ref in pmc.iterReferences():
        was_loaded = ref.isLoaded()
        if was_loaded:
            ref.unload()

        for edit in ref.getReferenceEdits():
            if any(s in edit for s in parameters):
                try:
                    pmc.ReferenceEdit(edit, fileReference=ref).remove(force=True)
                except RuntimeError as e:
                    logger.error("Could not remove edit: {}".format(edit))
                    logger.error(e)
                    success = False

        if was_loaded:
            ref.load()

    return success


def import_refs():
    logger.debug("Importing all References")
    success = True

    for ref in pmc.iterReferences():
        try:
            ref.importContents()
        except RuntimeError as e:
            logger.error("Could not import ref: {}".format(ref.namespace))
            logger.error(e)
            success = False

    return success


def create_tx():
    logger.debug("Update Tx Files")
    import mtoa.ui.arnoldmenu as arnoldmenu
    arnoldmenu.arnoldUpdateTx()
    return True


def publish_ass():
    logger.debug("ASS PUBLISH EXPORT")

    try:
        return scene_control.get_instance().publish_ass()
    except RuntimeError as e:
        logger.error("Could not export ass!")
        logger.error(e)
        return False
