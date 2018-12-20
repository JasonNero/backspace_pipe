import pymel.core as pmc
from backspace_pipe import logging_control
import os

# pipeline_re = re.compile(r"((\w+))_((MDL)|(SHD)|(RIG)|(ANI)|(LGT)|(SET))_REF")


logger = logging_control.get_logger()


def switch(curr_dep, new_dep, replace=True, grouped=False):
    curr_dep = curr_dep.upper()
    new_dep = new_dep.upper()

    error_counter = 0

    for ref in pmc.iterReferences():
        if ref.isLoaded():
            logger.debug("now processing... " + ref.refNode)

            # Get Path
            old_path = ref.path

            # Generate new Path
            if new_dep == "ASS":
                new_path = old_path.replace("_{}_REF.ma".format(curr_dep), "_SHD_REF.ass")
            else:
                new_path = old_path.replace("_{}_REF.ma".format(curr_dep), "_{}_REF.ma".format(new_dep))

            # Continue with next element if the wanted department could not be found
            if not os.path.isfile(new_path):
                logger.warning("no file for new department found")
                continue

            namespace = new_path.split(".")[0].split("/")[-1]

            if grouped:
                top_grps = pmc.ls(str(ref.refNode) + "group")
                if len(top_grps) == 0:
                    logger.warning("could not find the top_grp for the current ref: {}".format(ref.refNode))
                    error_counter += 1
                    continue
                else:
                    top_grp = top_grps[0]

            if replace:
                # Replace file+namespace+grpname Workflow

                # ref.load(new_path)
                ref.replaceWith(new_path)
                ref.refNode.unlock()

                ref.namespace = namespace
                pmc.rename(ref.refNode, str(ref.refNode).replace(curr_dep, new_dep))

                if grouped:
                    top_grp.unlock()
                    pmc.rename(top_grp, str(top_grp).replace(curr_dep, new_dep))
                    top_grp.lock()

                ref.refNode.lock()
            else:
                if not grouped:
                    logger.error("not implemented")
                    return False

                # ASS Workflow
                new_ref = pmc.createReference(new_path, namespace=namespace, groupReference=True)
                new_grp = pmc.ls(new_ref.refNode + "group")[0]

                for node in pmc.listRelatives(new_grp, children=True):
                    pmc.parent(node, top_grp, relative=True)

                # Set StandIn Preview to Polywire (2) / Shaded (6) / BoundingBox (0)
                standin = pmc.ls(str(new_ref.namespace) + ":ArnoldStandInShape")[0]
                standin.mode.set(2)

                pmc.delete(new_grp)
                ref.remove()

    if error_counter == 0:
        return True
    else:
        return False
