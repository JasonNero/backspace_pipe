import pymel.core as pmc
import re

# pipeline_re = re.compile(r"((\w+))_((MDL)|(SHD)|(RIG)|(ANI)|(LGT)|(SET))_(((\d+)(_\w+)?)|REF)(.ma$)")
pipeline_re = re.compile(r"((\w+))_((MDL)|(SHD)|(RIG)|(ANI)|(LGT)|(SET))_REF")


def mdl_to_ass():
    for ref in pmc.iterReferences():
        if ref.isLoaded():
            top_grp = pmc.ls(ref.refNode + "group")[0]

            match = pipeline_re.search(str(top_grp))
            if match is not None:
                print(top_grp, match.group(3))
            else:
                print(top_grp, "no match")

            path = ref.path.replace("_MDL_REF.ma", "_SHD_REF.ass")
            namespace = path.split(".ass")[0].split("/")[-1]
            ass_ref = pmc.createReference(path, namespace=namespace, groupReference=True)
            ass_grp = pmc.ls(ass_ref.refNode + "group")[0]

            for node in pmc.listRelatives(ass_grp, children=True):
                pmc.parent(node, top_grp, relative=True)

            pmc.delete(ass_grp)
            ref.remove()
