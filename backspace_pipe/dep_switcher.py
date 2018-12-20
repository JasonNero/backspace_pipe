import pymel.core as pmc
import re
import os

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

            old_path = ref.path
            new_path = old_path.replace("_MDL_REF.ma", "_SHD_REF.ass")
            namespace = new_path.split(".ass")[0].split("/")[-1]

            # ASS Workflow
            ass_ref = pmc.createReference(new_path, namespace=namespace, groupReference=True)
            ass_grp = pmc.ls(ass_ref.refNode + "group")[0]

            for node in pmc.listRelatives(ass_grp, children=True):
                pmc.parent(node, top_grp, relative=True)

            pmc.delete(ass_grp)
            ref.remove()


def switch(curr_dep, new_dep, replace=True):
    curr_dep = curr_dep.upper()
    new_dep = new_dep.upper()

    for ref in pmc.iterReferences():
        if ref.isLoaded():
            print("now processing... " + ref.refNode)

            # Get Path
            old_path = ref.path

            # Generate new Path
            if new_dep == "ASS":
                new_path = old_path.replace("_SHD_REF.ma", "_SHD_REF.ass")
            else:
                new_path = old_path.replace("_{}_REF.ma".format(curr_dep), "_{}_REF.ma".format(new_dep))

            # Continue with next element if the wanted department could not be found
            if not os.path.isfile(new_path):
                print("no file for new department found")
                continue

            namespace = new_path.split(".ma")[0].split("/")[-1]
            top_grps = pmc.ls(ref.refNode + "group")
            if len(top_grps) == 0:
                print("could not find the top_grp for the current ref")
                continue
            else:
                top_grp = top_grps[0]

            match = pipeline_re.search(str(top_grp))
            if match is not None:
                print(top_grp, match.group(3))
                pass
            else:
                print(top_grp, "Could not find top grp for ref " + ref.refNode)
                continue

            if replace:
                # Replace file+namespace+grpname Workflow
                ref.refNode.unlock()
                top_grp.unlock()

                ref.load(new_path)
                ref.namespace = namespace
                pmc.rename(ref.refNode, str(ref.refNode).replace(curr_dep, new_dep))
                pmc.rename(top_grp, str(top_grp).replace(curr_dep, new_dep))

                top_grp.lock()
                ref.refNode.lock()
            else:
                # ASS Workflow
                new_ref = pmc.createReference(new_path, namespace=namespace, groupReference=True)
                new_grp = pmc.ls(new_ref.refNode + "group")[0]

                for node in pmc.listRelatives(new_grp, children=True):
                    pmc.parent(node, top_grp, relative=True)

                pmc.delete(new_grp)
                ref.remove()
