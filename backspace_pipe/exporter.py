import pymel.core as pmc
import os
import subprocess

from backspace_pipe import logging_control

logger = logging_control.get_logger()

# EXPORTER
def export_obj(force, transf, triangulate, smooth):
    initial_selection = pmc.ls(sl=True)

    # Duplicate and triangulate if wanted
    dup = None

    if smooth and triangulate:
        dup = pmc.duplicate(transf)
        pmc.polySmooth(dup, mth=0, sdt=2, ovb=1, ofb=1, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1)
        pmc.polyTriangulate(dup)
        pmc.select(dup)
    elif smooth:
        dup = pmc.duplicate(transf)
        pmc.polySmooth(dup, mth=0, sdt=2, ovb=1, ofb=1, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1)
        pmc.select(dup)
    elif triangulate:
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


def export_fbx(force, transf, triangulate, smooth):
    initial_selection = pmc.ls(sl=True)

    # Duplicate and triangulate if wanted
    dup = None

    if smooth and triangulate:
        dup = pmc.duplicate(transf)
        pmc.polySmooth(dup, mth=0, sdt=2, ovb=1, ofb=1, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1)
        pmc.polyTriangulate(dup)
        pmc.select(dup)
    elif smooth:
        dup = pmc.duplicate(transf)
        pmc.polySmooth(dup, mth=0, sdt=2, ovb=1, ofb=1, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1)
        pmc.select(dup)
    elif triangulate:
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


# MULTIPLE EXPORTS
def export_selected_obj(force, triangulate, smooth):
    selected = pmc.ls(sl=True, transforms=True)

    for transf in selected:
        export_obj(force=force, transf=transf, triangulate=triangulate, smooth=smooth)


def export_selected_fbx(force, triangulate, smooth):
    selected = pmc.ls(sl=True, transforms=True)

    for transf in selected:
        export_fbx(force=force, transf=transf, triangulate=triangulate, smooth=smooth)


# UTILITY
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
