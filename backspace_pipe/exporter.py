import pymel.core as pmc
import os
import subprocess

from backspace_pipe import logging_control

logger = logging_control.get_logger()


def export_obj(force, transf, triangulate):
    initial_selection = pmc.ls(sl=True)

    # Duplicate and triangulate if wanted
    dup = None
    if triangulate:
        dup = pmc.duplicate(transf)
        pmc.polyTriangulate(dup)
        pmc.select(dup)
    else:
        pmc.select(transf)

    export_path = build_export_path(transf=transf, extension=".obj")

    try:
        exported_file = pmc.exportSelected(export_path, force=force, preserveReferences=True, type="OBJExport", options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")

        # MAYA BUG WORKAROUND (.obj extension missing)
        if not exported_file[-4:] == ".obj":
            os.rename(exported_file, export_path)
            os.rename(exported_file + "mtl", exported_file + ".mtl")

        success = True
    except RuntimeError as e:
        logger.error("Could not export node {}".format(transf))
        logger.error(e)
        success = False

    # delete triangulated duplicate again (if created)
    if dup:
        pmc.delete(dup)

    pmc.select(initial_selection)

    return success


def export_fbx(force, transf, triangulate):
    initial_selection = pmc.ls(sl=True)

    # Duplicate and triangulate if wanted
    dup = None
    if triangulate:
        dup = pmc.duplicate(transf)
        pmc.polyTriangulate(dup)
        pmc.select(dup)
    else:
        pmc.select(transf)

    export_path = build_export_path(transf=transf, extension=".fbx")

    try:
        pmc.exportSelected(export_path, force=force, preserveReferences=True, type="FBX export")
        success = True
    except RuntimeError as e:
        logger.error("Could not export node {}".format(transf))
        logger.error(e)
        success = False

    # delete triangulated duplicate again (if created)
    if dup:
        pmc.delete(dup)

    pmc.select(initial_selection)

    return success


def export_selected_obj(force, triangulate):
    selected = pmc.ls(sl=True, transforms=True)

    for transf in selected:
        export_obj(force=force, transf=transf, triangulate=triangulate)


def export_selected_fbx(force, triangulate):
    selected = pmc.ls(sl=True, transforms=True)

    for transf in selected:
        export_fbx(force=force, transf=transf, triangulate=triangulate)


def build_export_path(transf, extension):
    scene_path = pmc.sceneName()
    scene_name = scene_path.splitext()[0].split("/")[-1]
    export_folder = scene_path.parent.parent.parent / "Export"
    export_path = str(export_folder / scene_name + "__" + transf.shortName() + extension)
    return export_path


def explore_export_folder():
    scene_path = pmc.sceneName()
    export_folder = scene_path.parent.parent.parent / "Export"
    subprocess.Popen('explorer "{}"'.format(export_folder))